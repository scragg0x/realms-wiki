# Monkey patch stdlib.
import gevent.monkey
gevent.monkey.patch_all(aggressive=False)

# Set default encoding to UTF-8
import sys

reload(sys)
# noinspection PyUnresolvedReferences
sys.setdefaultencoding('utf-8')

# Silence Sentry and Requests.
import logging
logging.getLogger().setLevel(logging.INFO)
logging.getLogger('raven').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)

import time
import sys
import json
import httplib
import traceback
from flask import Flask, request, render_template, url_for, redirect, session, flash, g
from flask.ctx import _AppCtxGlobals
from flask.ext.script import Manager
from flask.ext.login import LoginManager
from werkzeug.routing import BaseConverter
from werkzeug.utils import cached_property
from werkzeug.exceptions import HTTPException

from realms import config
from realms.lib.ratelimit import get_view_rate_limit, ratelimiter
from realms.lib.session import RedisSessionInterface
from realms.lib.wiki import Wiki
from realms.lib.util import to_canonical, remove_ext, mkdir_safe, gravatar_url, to_dict


class AppCtxGlobals(_AppCtxGlobals):

    @cached_property
    def current_user(self):
        return session.get('user') if session.get('user') else {'username': 'Anon'}

    @cached_property
    def current_wiki(self):
        return Wiki(config.WIKI_PATH)


class Application(Flask):
    app_ctx_globals_class = AppCtxGlobals

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO')

        if path_info and len(path_info) > 1 and path_info.endswith('/'):
            environ['PATH_INFO'] = path_info[:-1]

        scheme = environ.get('HTTP_X_SCHEME')

        if scheme:
            environ['wsgi.url_scheme'] = scheme

        real_ip = environ.get('HTTP_X_REAL_IP')

        if real_ip:
            environ['REMOTE_ADDR'] = real_ip

        return super(Application, self).__call__(environ, start_response)

    def discover(self):
        IMPORT_NAME = 'realms.modules'
        FROMLIST = (
            'assets',
            'commands',
            'models',
            'views',
        )

        start_time = time.time()

        __import__(IMPORT_NAME, fromlist=FROMLIST)

        for module_name in self.config['MODULES']:
            sources = __import__('%s.%s' % (IMPORT_NAME, module_name), fromlist=FROMLIST)

            # Blueprint
            if hasattr(sources, 'views'):
                self.register_blueprint(sources.views.blueprint)

            # Flask-Script
            if hasattr(sources, 'commands'):
                manager.add_command(module_name, sources.commands.manager)

        print >> sys.stderr, ' * Ready in %.2fms' % (1000.0 * (time.time() - start_time))

    def make_response(self, rv):
        if rv is None:
            rv = '', httplib.NO_CONTENT
        elif not isinstance(rv, tuple):
            rv = rv,

        rv = list(rv)

        if isinstance(rv[0], (list, dict)):
            rv[0] = self.response_class(json.dumps(rv[0]), mimetype='application/json')

        return super(Application, self).make_response(tuple(rv))


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



app = Application(__name__)
app.config.from_object('realms.config')
app.session_interface = RedisSessionInterface()
app.url_map.converters['regex'] = RegexConverter
app.url_map.strict_slashes = False
app.debug = config.DEBUG

manager = Manager(app)

login_manager = LoginManager()
login_manager.init_app(app)


def error_handler(e):
    try:
        if isinstance(e, HTTPException):
            status_code = e.code
            message = e.description if e.description != type(e).description else None
            tb = None
        else:
            status_code = httplib.INTERNAL_SERVER_ERROR
            message = None
            tb = traceback.format_exc() if g.current_user.staff else None

        if request.is_xhr or request.accept_mimetypes.best in ['application/json', 'text/javascript']:
            response = {
                'message': message,
                'traceback': tb,
            }
        else:
            response = render_template('errors/error.html',
                                       title=httplib.responses[status_code],
                                       status_code=status_code,
                                       message=message,
                                       traceback=tb)
    except HTTPException as e2:
        return error_handler(e2)

    return response, status_code

for status_code in httplib.responses:
    if status_code >= 400:
        app.register_error_handler(status_code, error_handler)

from realms.lib.assets import register, assets
assets.init_app(app)
assets.app = app
assets.debug = config.DEBUG

register('main',
         'vendor/jquery/jquery.js',
         'vendor/components-underscore/underscore.js',
         'vendor/components-bootstrap/js/bootstrap.js',
         'vendor/handlebars/handlebars.js',
         'vendor/showdown/src/showdown.js',
         'vendor/showdown/src/extensions/table.js',
         'js/wmd.js',
         'js/html-sanitizer-minified.js',  # don't minify
         'vendor/highlightjs/highlight.pack.js',
         'vendor/parsleyjs/dist/parsley.js',
         'js/main.js')


@app.before_request
def init_g():
    g.assets = ['main']


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


if config.RELATIVE_PATH:
    @app.route("/")
    def root():
        return redirect(url_for(config.ROOT_ENDPOINT))


app.discover()

