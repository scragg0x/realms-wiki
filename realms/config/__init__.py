import os
import json
from urlparse import urlparse

APP_PATH = os.path.dirname(__file__) + "/../.."
USER_HOME = os.path.expanduser("~")

ENV = 'DEV'

DEBUG = True
ASSETS_DEBUG = True
SQLALCHEMY_ECHO = True

PORT = 5000
BASE_URL = 'http://realms.dev'
SITE_TITLE = "Realms"

DB_URI = 'sqlite:///%s/wiki.db' % USER_HOME

CACHE_TYPE = 'simple'

# Redis Example
"""
CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = '127.0.0.1'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_DB = '0'
"""

# Get ReCaptcha Keys for your domain here:
# https://www.google.com/recaptcha/admin#whyrecaptcha
RECAPTCHA_ENABLE = False
RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = "6LfYbPkSAAAAAB4a2lG2Y_Yjik7MG9l4TDzyKUao"
RECAPTCHA_PRIVATE_KEY = "6LfYbPkSAAAAAG-KlkwjZ8JLWgwc9T0ytkN7lWRE"
RECAPTCHA_OPTIONS = {}

SECRET_KEY = 'K3dRq1q9eN72GJDkgvyshFVwlqHHCyPI'

# Path on file system where wiki data will reside
WIKI_PATH = os.path.join(APP_PATH, 'wiki')

# Name of page that will act as home
WIKI_HOME = 'home'

ALLOW_ANON = True
REGISTRATION_ENABLED = True

# Used by Flask-Login
LOGIN_DISABLED = ALLOW_ANON

# Page names that can't be modified
WIKI_LOCKED_PAGES = []
# Depreciated variable name
LOCKED = WIKI_LOCKED_PAGES

ROOT_ENDPOINT = 'wiki.page'

try:
    with open(os.path.join(APP_PATH, 'config.json')) as f:
        __settings = json.load(f)
        for k in ['APP_PATH', 'USER_HOME']:
            if k in __settings:
                del __settings[k]
        globals().update(__settings)
except IOError:
    pass

if BASE_URL.endswith('/'):
    BASE_URL = BASE_URL[-1]

SQLALCHEMY_DATABASE_URI = DB_URI

_url = urlparse(BASE_URL)
RELATIVE_PATH = _url.path

if ENV != "DEV":
    DEBUG = False
    ASSETS_DEBUG = False
    SQLALCHEMY_ECHO = False

MODULES = ['wiki', 'auth']
