import os
import json
from urlparse import urlparse

ENV = 'DEV'

DEBUG = True
ASSETS_DEBUG = True

PORT = 80
BASE_URL = 'http://realms.dev'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = '0'

SECRET = 'K3dRq1q9eN72GJDkgvyshFVwlqHHCyPI'

WIKI_PATH = '/home/deploy/wiki'
WIKI_HOME = 'home'

ALLOW_ANON = True

ROOT_ENDPOINT = 'wiki.page'

with open(os.path.join(os.path.dirname(__file__) + "/../../", 'config.json')) as f:
    __settings = json.load(f)
    globals().update(__settings)

# String trailing slash
if BASE_URL.endswith('/'):
    BASE_URL = BASE_URL[-1]

_url = urlparse(BASE_URL)
RELATIVE_PATH = _url.path

if ENV != "DEV":
    DEBUG = False
    ASSETS_DEBUG = False

MODULES = ['wiki', 'auth']
