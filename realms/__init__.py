import sys

# Set default encoding to UTF-8
reload(sys)
# noinspection PyUnresolvedReferences
sys.setdefaultencoding('utf-8')

import base64
import time
import json
import httplib
import traceback
import click
from flask import Flask, request, render_template, url_for, redirect, g
from flask.ext.cache import Cache
from flask.ext.login import LoginManager, current_user
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from flask_ldap_login import LDAPLoginManager
from functools import update_wrapper
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import HTTPException
from sqlalchemy.ext.declarative import declarative_base

from .modules.search.models import Search
from .lib.util import to_canonical, remove_ext, mkdir_safe, gravatar_url, to_dict
from .lib.hook import HookModelMeta, HookMixin
from .lib.util import is_su, in_virtualenv
from .version import __version__


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
            'hooks'
        )

        start_time = time.time()

        __import__(import_name, fromlist=fromlist)

        for module_name in self.config['MODULES']:
            sources = __import__('%s.%s' % (import_name, module_name), fromlist=fromlist)

            if hasattr(sources, 'init'):
                sources.init(self)

            # Blueprint
            if hasattr(sources, 'views'):
                self.register_blueprint(sources.views.blueprint, url_prefix=self.config['RELATIVE_PATH'])

            # Click
            if hasattr(sources, 'commands'):
                cli.add_command(sources.commands.cli, name=module_name)

            # Hooks
            if hasattr(sources, 'hooks'):
                if hasattr(sources.hooks, 'before_request'):
                    self.before_request(sources.hooks.before_request)

                if hasattr(sources.hooks, 'before_first_request'):
                    self.before_first_request(sources.hooks.before_first_request)

                    # print >> sys.stderr, ' * Ready in %.2fms' % (1000.0 * (time.time() - start_time))

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


class MyLDAPLoginManager(LDAPLoginManager):
    @property
    def attrlist(self):
        # the parent method doesn't always work
        return None


class RegexConverter(BaseConverter):
    """ Enables Regex matching on endpoints
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


def create_app(config=None):
    app = Application(__name__)
    app.config.from_object('realms.config')
    app.url_map.converters['regex'] = RegexConverter
    app.url_map.strict_slashes = False

    login_manager.init_app(app)
    db.init_app(app)
    cache.init_app(app)
    assets.init_app(app)
    search.init_app(app)
    ldap.init_app(app)

    db.Model = declarative_base(metaclass=HookModelMeta, cls=HookMixin)

    for status_code in httplib.responses:
        if status_code >= 400:
            app.register_error_handler(status_code, error_handler)

    @app.before_request
    def init_g():
        g.assets = dict(css=['main.css'], js=['main.js'])

    @app.template_filter('datetime')
    def _jinja2_filter_datetime(ts, fmt=None):
        return time.strftime(
            fmt or app.config.get('DATETIME_FORMAT', '%b %d, %Y %I:%M %p'),
            time.localtime(ts)
        )

    @app.template_filter('b64encode')
    def _jinja2_filter_b64encode(s):
        return base64.urlsafe_b64encode(s).rstrip("=")

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    if app.config.get('RELATIVE_PATH'):
        @app.route("/")
        def root():
            return redirect(url_for(app.config.get('ROOT_ENDPOINT')))

    app.discover()

    # This will be removed at some point
    with app.app_context():
        if app.config.get('DB_URI'):
            db.metadata.create_all(db.get_engine(app))

    return app

# Init plugins here if possible
login_manager = LoginManager()

db = SQLAlchemy()
cache = Cache()
assets = Assets()
search = Search()
ldap = MyLDAPLoginManager()

assets.register('main.js',
                'vendor/jquery/dist/jquery.js',
                'vendor/components-bootstrap/js/bootstrap.js',
                'vendor/handlebars/handlebars.js',
                'vendor/js-yaml/dist/js-yaml.js',
                'vendor/marked/lib/marked.js',
                'js/html-sanitizer-minified.js',  # don't minify?
                'vendor/highlightjs/highlight.pack.js',
                'vendor/parsleyjs/dist/parsley.js',
                'vendor/datatables/media/js/jquery.dataTables.js',
                'vendor/datatables-plugins/integration/bootstrap/3/dataTables.bootstrap.js',
                'js/hbs-helpers.js',
                'js/mdr.js',
                'js/main.js')

assets.register('main.css',
                'vendor/bootswatch-dist/css/bootstrap.css',
                'vendor/components-font-awesome/css/font-awesome.css',
                'vendor/highlightjs/styles/github.css',
                'vendor/datatables-plugins/integration/bootstrap/3/dataTables.bootstrap.css',
                'css/style.css')


def with_appcontext(f):
    """Wraps a callback so that it's guaranteed to be executed with the
    script's application context.  If callbacks are registered directly
    to the ``app.cli`` object then they are wrapped with this function
    by default unless it's disabled.
    """
    @click.pass_context
    def decorator(__ctx, *args, **kwargs):
        with create_app().app_context():
            return __ctx.invoke(f, *args, **kwargs)
    return update_wrapper(decorator, f)


class AppGroup(click.Group):
    """This works similar to a regular click :class:`~click.Group` but it
    changes the behavior of the :meth:`command` decorator so that it
    automatically wraps the functions in :func:`with_appcontext`.
    Not to be confused with :class:`FlaskGroup`.
    """

    def command(self, *args, **kwargs):
        """This works exactly like the method of the same name on a regular
        :class:`click.Group` but it wraps callbacks in :func:`with_appcontext`
        unless it's disabled by passing ``with_appcontext=False``.
        """
        wrap_for_ctx = kwargs.pop('with_appcontext', True)

        def decorator(f):
            if wrap_for_ctx:
                f = with_appcontext(f)
            return click.Group.command(self, *args, **kwargs)(f)
        return decorator

    def group(self, *args, **kwargs):
        """This works exactly like the method of the same name on a regular
        :class:`click.Group` but it defaults the group class to
        :class:`AppGroup`.
        """
        kwargs.setdefault('cls', AppGroup)
        return click.Group.group(self, *args, **kwargs)

flask_cli = AppGroup()


@flask_cli.group()
def cli():
    pass
