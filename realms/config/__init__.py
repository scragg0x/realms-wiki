import os
import json
from urlparse import urlparse
from realms.lib.util import in_vagrant


def update(data):
    conf = read()
    conf.update(data)
    return save(data)


def read():
    conf = dict()

    for k, v in os.environ.items():
        if k.startswith('REALMS_'):
            conf[k[7:]] = v

    loc = get_path()

    if loc:
        with open(loc) as f:
            conf.update(json.load(f))

    for k in ['APP_PATH', 'USER_HOME']:
        if k in conf:
            del conf[k]

    return conf


def save(conf):
    loc = get_path(check_write=True)
    with open(loc, 'w') as f:
        f.write(json.dumps(conf, sort_keys=True, indent=4, separators=(',', ': ')).strip() + '\n')
    return loc


def get_path(check_write=False):
    """Find config path
    """
    for loc in os.curdir, os.path.expanduser("~"), "/etc/realms-wiki":
        if not loc:
            continue
        path = os.path.join(loc, "realms-wiki.json")
        if os.path.isfile(path):
            # file exists
            if not check_write:
                # Don't care if I can write
                return path

            if os.access(path, os.W_OK):
                # Has write access, ok!
                return path
        elif os.path.isdir(loc) and check_write:
            # dir exists file doesn't
            if os.access(loc, os.W_OK):
                # can write file
                return path
    return None


APP_PATH = os.path.abspath(os.path.dirname(__file__) + "/../..")
USER_HOME = os.path.abspath(os.path.expanduser("~"))

# Best to change to /var/run
PIDFILE = "/tmp/realms-wiki.pid"

ENV = 'DEV'

DEBUG = True
ASSETS_DEBUG = True
SQLALCHEMY_ECHO = False

HOST = "0.0.0.0"
PORT = 5000
BASE_URL = 'http://localhost'
SITE_TITLE = "Realms"

# https://pythonhosted.org/Flask-SQLAlchemy/config.html#connection-uri-format
DB_URI = 'sqlite:////tmp/wiki.db'
# DB_URI = 'mysql://scott:tiger@localhost/mydatabase'
# DB_URI = 'postgresql://scott:tiger@localhost/mydatabase'
# DB_URI = 'oracle://scott:tiger@127.0.0.1:1521/sidname'
# DB_URI = 'crate://'

# LDAP = {
#     'URI': '',
#
#     # This BIND_DN/BIND_PASSWORD default to '', this is shown here for demonstrative purposes
#     # The values '' perform an anonymous bind so we may use search/bind method
#     'BIND_DN': '',
#     'BIND_AUTH': '',
#
#     # Adding the USER_SEARCH field tells the flask-ldap-login that we are using
#     # the search/bind method
#     'USER_SEARCH': {'base': 'dc=example,dc=com', 'filter': 'uid=%(username)s'},
#
#     # Map ldap keys into application specific keys
#     'KEY_MAP': {
#         'name': 'cn',
#         'company': 'o',
#         'location': 'l',
#         'email': 'mail',
#     }
# }

# OAUTH = {
#     'twitter': {
#         'key': '',
#         'secret': ''
#    },
#    'github': {
#        'key': '',
#        'secret': ''
#    }
# }

CACHE_TYPE = 'simple'

# Redis
# CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = '127.0.0.1'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_DB = '0'

# Memcached
# CACHE_TYPE = 'memcached'
CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']

SEARCH_TYPE = 'simple'  # simple is not good for large wikis

# SEARCH_TYPE = 'elasticsearch'
ELASTICSEARCH_URL = 'http://127.0.0.1:9200'
ELASTICSEARCH_FIELDS = ["name"]

# SEARCH_TYPE = 'whoosh'
WHOOSH_INDEX = '/tmp/whoosh'
WHOOSH_LANGUAGE = 'en'

# Get ReCaptcha Keys for your domain here:
# https://www.google.com/recaptcha/admin#whyrecaptcha
RECAPTCHA_ENABLE = False
RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = "6LfYbPkSAAAAAB4a2lG2Y_Yjik7MG9l4TDzyKUao"
RECAPTCHA_PRIVATE_KEY = "6LfYbPkSAAAAAG-KlkwjZ8JLWgwc9T0ytkN7lWRE"
RECAPTCHA_OPTIONS = {}

SECRET_KEY = 'CHANGE_ME'

# Path on file system where wiki data will reside
WIKI_PATH = '/tmp/wiki'

# Name of page that will act as home
WIKI_HOME = 'home'

AUTH_LOCAL_ENABLE = True
ALLOW_ANON = True
REGISTRATION_ENABLED = True
PRIVATE_WIKI = False

# None, firepad, and/or togetherjs
COLLABORATION = 'togetherjs'

# Required for firepad
FIREBASE_HOSTNAME = None

# Page names that can't be modified
WIKI_LOCKED_PAGES = []

ROOT_ENDPOINT = 'wiki.page'

# Used by Flask-Login
LOGIN_DISABLED = ALLOW_ANON

# Depreciated variable name
LOCKED = WIKI_LOCKED_PAGES[:]

if BASE_URL.endswith('/'):
    BASE_URL = BASE_URL[:-1]

SQLALCHEMY_DATABASE_URI = DB_URI

_url = urlparse(BASE_URL)
RELATIVE_PATH = _url.path

if in_vagrant():
    # sendfile doesn't work well with Virtualbox shared folders
    USE_X_SENDFILE = False

if ENV != "DEV":
    DEBUG = False
    ASSETS_DEBUG = False
    SQLALCHEMY_ECHO = False

MODULES = ['wiki', 'search', 'auth']

globals().update(read())

if globals().get('AUTH_LOCAL_ENABLE'):
    MODULES.append('auth.local')

if globals().get('OAUTH'):
    MODULES.append('auth.oauth')

if globals().get('LDAP'):
    MODULES.append('auth.ldap')
