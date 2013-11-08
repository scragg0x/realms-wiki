import logging
import os
import time
from threading import Lock

import rethinkdb as rdb
from flask import Flask, g, request, render_template, url_for, redirect, flash, session
from flask.ctx import _AppCtxGlobals
from flask.ext.login import LoginManager, login_required
from flask.ext.assets import Environment, Bundle
from werkzeug.routing import BaseConverter
from werkzeug.utils import cached_property

import config
from realms.lib.ratelimit import get_view_rate_limit, ratelimiter
from realms.lib.session import RedisSessionInterface
from realms.lib.wiki import Wiki
from realms.lib.util import to_canonical, remove_ext, mkdir_safe, gravatar_url
from realms.lib.services import db
from models import Site, User, CurrentUser


# Flask instance container
instances = {}

# Flask extension objects
login_manager = LoginManager()
assets = Environment()


class AppCtxGlobals(_AppCtxGlobals):

    @cached_property
    def current_user(self):
        return session.get('user') if session.get('user') else {'username': 'Anon'}


class Application(Flask):
    app_ctx_globals_class = AppCtxGlobals


class SubdomainDispatcher(object):
    """
    Application factory
    """
    def __init__(self, domain, create_app):
        self.domain = domain
        self.create_app = create_app
        self.lock = Lock()

    def get_application(self, host):
        host = host.split(':')[0]
        assert host.endswith(self.domain), 'Configuration error'
        subdomain = host[:-len(self.domain)].rstrip('.')
        with self.lock:
            app = instances.get(subdomain)
            if app is None:
                app = self.create_app(subdomain)
                instances[subdomain] = app
            return app

    def __call__(self, environ, start_response):
        app = self.get_application(environ['HTTP_HOST'])
        return app(environ, start_response)


def init_db(dbname):
    """
    Assures DB has minimal setup
    """
    if not dbname in rdb.db_list().run(db):
        print "Creating DB %s" % dbname
        rdb.db_create(dbname).run(db)

    for tbl in ['sites', 'users', 'pages']:
        if not tbl in rdb.table_list().run(db):
            rdb.table_create(tbl).run(db)

    if not 'name' in rdb.table('sites').index_list().run(db):
        rdb.table('sites').index_create('name').run(db)

    for i in ['username', 'email']:
        if not i in rdb.table('users').index_list().run(db):
            rdb.table('users').index_create(i).run(db)

    s = Site()
    if not s.get_by_name('_'):
        s.create(name='_', repo='_')


class RegexConverter(BaseConverter):
    """
    Enables Regex matching on endpoints
    """
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def redirect_url(referrer=None):
    if not referrer:
        referrer = request.referrer
    return request.args.get('next') or referrer or url_for('index')


def format_subdomain(s):
    if not config.repos['enable_subrepos']:
        return ""
    s = s.lower()
    s = to_canonical(s)
    if s in config.repos['forbidden_subrepos']:
        # Not allowed
        s = ""
    return s


def make_app(subdomain):
    subdomain = format_subdomain(subdomain)
    if subdomain and not Wiki.is_registered(subdomain):
        return redirect("http://%s/_new/?site=%s" % (config.hostname, subdomain))
    return create_app(subdomain)


def create_app(subdomain=None):
    app = Application(__name__)
    app.config.update(config.flask)
    app.debug = (config.ENV is not 'PROD')
    app.secret_key = config.secret_key
    app.static_path = os.sep + 'static'
    app.session_interface = RedisSessionInterface()
    app.url_map.converters['regex'] = RegexConverter

    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return CurrentUser(user_id)

    assets.init_app(app)
    if config.ENV is 'PROD':
        if 'js_common' not in assets._named_bundles:
            assets.register('js_common', Bundle('packed-common.js'))
        if 'js_editor' not in assets._named_bundles:
            assets.register('js_editor', Bundle('packed-editor.js'))
    else:
        if 'js_common' not in assets._named_bundles:
            js = Bundle(
                Bundle('vendor/jquery/jquery.js',
                       'vendor/components-underscore/underscore.js',
                       'vendor/components-bootstrap/js/bootstrap.js',
                       'vendor/handlebars/handlebars.js',
                       'vendor/showdown/src/showdown.js',
                       'vendor/showdown/src/extensions/table.js',
                       'js/wmd.js',
                       filters='closure_js'),
                'js/html-sanitizer-minified.js',
                'vendor/highlightjs/highlight.pack.js',
                Bundle('js/main.js', filters='closure_js'),
                output='packed-common.js')
            assets.register('js_common', js)

        if 'js_editor' not in assets._named_bundles:
            js = Bundle('js/ace/ace.js',
                        'js/ace/mode-markdown.js',
                        'vendor/keymaster/keymaster.js',
                        'js/dillinger.js',
                        filters='closure_js', output='packed-editor.js')
            assets.register('js_editor', js)

    repo_dir = config.repos['dir']
    repo_name = subdomain if subdomain else "_"

    w = Wiki(repo_dir + "/" + repo_name)

    @app.after_request
    def inject_x_rate_headers(response):
        limit = get_view_rate_limit()
        if limit and limit.send_x_headers:
            h = response.headers
            h.add('X-RateLimit-Remaining', str(limit.remaining))
            h.add('X-RateLimit-Limit', str(limit.limit))
            h.add('X-RateLimit-Reset', str(limit.reset))
        return response

    @app.template_filter('datetime')
    def _jinja2_filter_datetime(ts):
        return time.strftime('%b %d, %Y %I:%M %p', time.localtime(ts))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def page_error(e):
        logging.exception(e)
        return render_template('errors/500.html'), 500

    @app.route("/")
    @ratelimiter(limit=50, per=60)
    def root():
        return render('home')

    @app.route("/home")
    def home():
        return redirect(url_for('root'))

    @app.route("/_account/")
    @login_required
    def account():
        return render_template('account/index.html')

    @app.route("/_new/", methods=['GET', 'POST'])
    @login_required
    def new_wiki():
        if request.method == 'POST':
            wiki_name = to_canonical(request.form['name'])

            if Wiki.is_registered(wiki_name):
                flash("Site already exists")
                return redirect(redirect_url())
            else:
                s = Site()
                s.create(name=wiki_name, repo=wiki_name, founder=g.current_user.get('id'))
                instances.pop(wiki_name, None)
                return redirect('http://%s.%s' % (wiki_name, config.hostname))
        else:
            return render_template('_new/index.html')

    @app.route("/_logout/")
    def logout():
        User.logout()
        return redirect(url_for('root'))

    @app.route("/_commit/<sha>/<name>")
    def commit_sha(name, sha):
        cname = to_canonical(name)

        data = w.get_page(cname, sha=sha)
        if data:
            return render_template('page/page.html', name=name, page=data, commit=sha)
        else:
            return redirect('/_create/'+cname)

    @app.route("/_compare/<name>/<regex('[^.]+'):fsha><regex('\.{2,3}'):dots><regex('.+'):lsha>")
    def compare(name, fsha, dots, lsha):
        diff = w.compare(name, fsha, lsha)
        return render_template('page/compare.html', name=name, diff=diff, old=fsha, new=lsha)

    @app.route("/_revert", methods=['POST'])
    def revert():
        if request.method == 'POST':
            name = request.form.get('name')
            commit = request.form.get('commit')
            cname = to_canonical(name)
            w.revert_page(name, commit, message="Reverting %s" % cname, username=g.current_user.get('username'))
            flash('Page reverted', 'success')
            return redirect("/" + cname)

    @app.route("/_register", methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            if User.register(request.form.get('username'), request.form.get('email'), request.form.get('password')):
                return redirect(url_for('root'))
            else:
                # Login failed
                return redirect(url_for('register'))
        else:
            return render_template('account/register.html')

    @app.route("/_login", methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            if User.auth(request.form['email'], request.form['password']):
                return redirect(redirect_url(referrer=url_for('root')))
            else:
                flash("Email or Password invalid")
                return redirect("/_login")
        else:
            return render_template('account/login.html')

    @app.route("/_history/<name>")
    def history(name):
        history = w.get_history(name)
        return render_template('page/history.html', name=name, history=history)

    @app.route("/_edit/<name>", methods=['GET', 'POST'])
    def edit(name):
        data = w.get_page(name)
        cname = to_canonical(name)
        if request.method == 'POST':
            edit_cname = to_canonical(request.form['name'])
            if edit_cname.lower() != cname.lower():
                w.rename_page(cname, edit_cname)
            w.write_page(edit_cname, request.form['content'],
                         message=request.form['message'],
                         username=g.current_user.get('username'))
            return redirect("/" + edit_cname)
        else:
            if data:
                name = remove_ext(data['name'])
                content = data['data']
                return render_template('page/edit.html', name=name, content=content)
            else:
                return redirect('/_create/'+cname)

    @app.route("/_delete/<name>", methods=['POST'])
    @login_required
    def delete(name):
        pass

    @app.route("/_create/", methods=['GET', 'POST'])
    @app.route("/_create/<name>", methods=['GET', 'POST'])
    def create(name=None):
        cname = ""
        if name:
            cname = to_canonical(name)
            if w.get_page(cname):
                # Page exists, edit instead
                return redirect("/edit/" + cname)
        if request.method == 'POST':
            w.write_page(request.form['name'], request.form['content'],
                         message=request.form['message'],
                         create=True,
                         username=g.current_user.get('username'))
            return redirect("/" + cname)
        else:
            return render_template('page/edit.html', name=cname, content="")

    @app.route("/<name>")
    def render(name):
        cname = to_canonical(name)
        if cname != name:
            return redirect('/' + cname)

        data = w.get_page(cname)
        if data:
            return render_template('page/page.html', name=cname, page=data)
        else:
            return redirect('/_create/'+cname)

    return app