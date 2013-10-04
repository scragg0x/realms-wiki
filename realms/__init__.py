import logging
import os
import time

from flask import Flask, request, render_template, url_for, redirect, flash, session
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager, login_user, logout_user
from flask.ext.assets import Environment
from recaptcha.client import captcha
from werkzeug.routing import BaseConverter
from session import RedisSessionInterface
import config
from wiki import Wiki
from util import to_canonical, remove_ext, mkdir_safe, gravatar_url
from models import Site, User, CurrentUser


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def redirect_url():
    return request.args.get('next') or request.referrer or url_for('index')


def validate_captcha():
    response = captcha.submit(
        request.form['recaptcha_challenge_field'],
        request.form['recaptcha_response_field'],
        config.flask['RECAPTCHA_PRIVATE_KEY'],
        request.remote_addr)
    return response.is_valid


def create_app(subdomain=None):
    app = Flask(__name__)
    app.config.update(config.flask)
    app.debug = (config.ENV is not 'PROD')
    app.secret_key = config.secret_key
    app.static_path = os.sep + 'static'
    app.session_interface = RedisSessionInterface()
    app.url_map.converters['regex'] = RegexConverter

    bcrypt = Bcrypt(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return CurrentUser(user_id)

    assets = Environment(app)
    assets.url = app.static_url_path
    assets.directory = app.static_folder


    main_repo_dir = config.repos['main']
    repo_dir = config.repos['dir']

    w = Wiki(main_repo_dir) if not subdomain else Wiki(repo_dir + "/" + subdomain)


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
    def root():
        return render('home')
        #return redirect('/home')


    @app.route("/account/")
    def account():
        return render_template('account/index.html')


    @app.route("/_new/", methods=['GET', 'POST'])
    def new_wiki():
        if request.method == 'POST':
            # TODO validate wiki name
            wiki_name = request.form['name']
            s = Site()
            if s.get_by_name(wiki_name):
                flash("Site already exists")
                return redirect(redirect_url())
            else:
                Wiki(repo_dir + "/" + wiki_name)
                return redirect('http://%s.%s' % (wiki_name, config.hostname))
        else:
            return render_template('_new/index.html')


    @app.route("/logout/")
    def logout():
        logout_user()
        del session['user']
        return redirect(url_for('root'))

    @app.route("/commit/<sha>/<name>")
    def commit_sha(name, sha):
        cname = to_canonical(name)

        data = w.get_page(cname, sha=sha)
        if data:
            return render_template('page/page.html', page=data)
        else:
            return redirect('/create/'+cname)


    @app.route("/compare/<name>/<regex('[^.]+'):fsha><regex('\.{2,3}'):dots><regex('.+'):lsha>")
    def compare(name, fsha, dots, lsha):
        diff = w.compare(name, fsha, lsha)
        return render_template('page/compare.html', name=name, diff=diff)


    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            user = User()
            if user.get_by_email(request.form['email']):
                flash('Email is already taken')
                return redirect('/register')
            if user.get_by_username(request.form['username']):
                flash('Username is already taken')
                return redirect('/register')

            email = request.form['email'].lower()
            # Create user and login
            u = User.create(email=email,
                            username=request.form['username'],
                            password=bcrypt.generate_password_hash(request.form['password']),
                            avatar=gravatar_url(email))
            login_user(CurrentUser(u.id))
            return redirect("/")
        else:
            return render_template('account/register.html')


    @app.route("/login", methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            if User.auth(request.form['email'], request.form['password']):
                return redirect("/")
            else:
                flash("Email or Password invalid")
                return redirect("/login")
        else:
            return render_template('account/login.html')


    @app.route("/history/<name>")
    def history(name):
        history = w.get_history(name)
        return render_template('page/history.html', name=name, history=history)


    @app.route("/edit/<name>", methods=['GET', 'POST'])
    def edit(name):
        data = w.get_page(name)
        cname = to_canonical(name)
        if request.method == 'POST':
            edit_cname = to_canonical(request.form['name'])
            if edit_cname != cname:
                w.rename_page(cname, edit_cname)
            w.write_page(edit_cname, request.form['content'], message=request.form['message'])
            return redirect("/" + edit_cname)
        else:
            if data:
                name = remove_ext(data['name'])
                content = data['data']
                return render_template('page/edit.html', name=name, content=content)
            else:
                return redirect('/create/'+cname)


    @app.route("/delete/<name>", methods=['POST'])
    def delete(name):
        pass


    @app.route("/create/", methods=['GET', 'POST'])
    @app.route("/create/<name>", methods=['GET', 'POST'])
    def create(name=None):
        cname = ""
        if name:
            cname = to_canonical(name)
            if w.get_page(cname):
                # Page exists, edit instead
                return redirect("/edit/" + cname)
        if request.method == 'POST':
            w.write_page(request.form['name'], request.form['content'],  message=request.form['message'], create=True)
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
            return redirect('/create/'+cname)

    return app