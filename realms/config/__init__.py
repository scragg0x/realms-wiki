import socket

HOSTNAME = socket.gethostname()

if HOSTNAME.startswith('lsn-'):
    ENV = 'PROD'
else:
    ENV = 'DEV'

SQLALCHEMY_DATABASE_URI = 'postgresql://deploy:dbpassword@localhost:5432/realms'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

SECRET_KEY = 'K3dRq1q9eN72GJDkgvyshFVwlqHHCyPI'

REPO_DIR = '/home/deploy/repos'
REPO_MAIN_NAME = '_'
REPO_FORBIDDEN_NAMES = ['api', 'www']
REPO_ENABLE_SUBDOMAIN = True

RECAPTCHA_PUBLIC_KEY = '6LfoxeESAAAAAGNaeWnISh0GTgDk0fBnr6Bo2Tfk'
RECAPTCHA_PRIVATE_KEY = '6LfoxeESAAAAABFzdCs0hNIIyeb42mofV-Ndd2_2'
RECAPTCHA_OPTIONS = {'theme': 'clean'}

ROOT_ENDPOINT = 'wiki.page'
WIKI_HOME = 'home'

MODULES = [
    'wiki',
    'auth'
]

if ENV is 'PROD':
    PORT = 80
    DOMAIN = 'realms.io'
else:
    DEBUG = True
    ASSETS_DEBUG = True
    DOMAIN = 'realms.dev'
    PORT = 8000