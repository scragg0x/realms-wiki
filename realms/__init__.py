# Monkey patch stdlib.
import gevent.monkey
gevent.monkey.patch_all(aggressive=False)

# Set default encoding to UTF-8
import sys

reload(sys)
# noinspection PyUnresolvedReferences
sys.setdefaultencoding('utf-8')

import time
import sys
import json
import httplib
import traceback
from flask import Flask, request, render_template, url_for, redirect, g
from flask.ext.cache import Cache
from flask.ext.script import Manager
from flask.ext.login import LoginManager, current_user
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import HTTPException

from realms import config
from realms.lib.util import to_canonical, remove_ext, mkdir_safe, gravatar_url, to_dict


class Application(Flask):

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
        import_name = 'realms.modules'
        fromlist = (
            'assets',
            'commands',
            'models',
            'views',
        )

        start_time = time.time()

        __import__(import_name, fromlist=fromlist)

        for module_name in self.config['MODULES']:
            sources = __import__('%s.%s' % (import_name, module_name), fromlist=fromlist)

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


class Assets(Environment):
    default_filters = {'js': 'rjsmin', 'css': 'cleancss'}
    default_output = {'js': 'assets/%(version)s.js', 'css': 'assets/%(version)s.css'}

    def register(self, name, *args, **kwargs):
        ext = args[0].split('.')[-1]
        filters = kwargs.get('filters', self.default_filters[ext])
        output = kwargs.get('output', self.default_output[ext])

        return super(Assets, self).register(name, Bundle(*args, filters=filters, output=output))


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


def error_handler(e):
    try:
        if isinstance(e, HTTPException):
            status_code = e.code
            message = e.description if e.description != type(e).description else None
            tb = None
        else:
            status_code = httplib.INTERNAL_SERVER_ERROR
            message = None
            tb = traceback.format_exc() if current_user.admin else None

        if request.is_xhr or request.accept_mimetypes.best in ['application/json', 'text/javascript']:
            response = {
                'message': message,
                'traceback': tb
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


def create_app():
    app = Application(__name__)
    app.config.from_object('realms.config')
    app.url_map.converters['regex'] = RegexConverter
    app.url_map.strict_slashes = False

    for status_code in httplib.responses:
        if status_code >= 400:
            app.register_error_handler(status_code, error_handler)

    @app.before_request
    def init_g():
        g.assets = dict(css=['main.css'], js=['main.js'])

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

    return app

app = create_app()

# Init plugins here if possible
manager = Manager(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

db = SQLAlchemy(app)
cache = Cache(app)

assets = Assets(app)
assets.register('main.js',
                'vendor/jquery/jquery.js',
                'vendor/components-underscore/underscore.js',
                'vendor/components-bootstrap/js/bootstrap.js',
                'vendor/handlebars/handlebars.js',
                'vendor/showdown/src/showdown.js',
                'vendor/showdown/src/extensions/table.js',
                'js/wmd.js',
                'js/html-sanitizer-minified.js',  # don't minify?
                'vendor/highlightjs/highlight.pack.js',
                'vendor/parsleyjs/dist/parsley.js',
                'js/main.js')

assets.register('main.css',
                'css/bootstrap/flatly.css',
                'css/font-awesome.min.css',
                'vendor/highlightjs/styles/github.css',
                'css/style.css')

app.discover()

# Should be called explicitly during install?
db.create_all()






