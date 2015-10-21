from flask_login import login_user
from flask_oauthlib.client import OAuth

from realms import config
from ..models import BaseUser

oauth = OAuth()

users = {}

providers = {
    'twitter': {
        'oauth': dict(
            base_url='https://api.twitter.com/1.1/',
            request_token_url='https://api.twitter.com/oauth/request_token',
            access_token_url='https://api.twitter.com/oauth/access_token',
            authorize_url='https://api.twitter.com/oauth/authenticate',
            access_token_method='GET'),
        'button': '<a href="/login/oauth/twitter" class="btn btn-default"><i class="fa fa-twitter"></i> Twitter</a>'
    },
    'github': {
        'oauth': dict(
            request_token_params={'scope': 'user:email'},
            base_url='https://api.github.com/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize'),
        'button': '<a href="/login/oauth/github" class="btn btn-default"><i class="fa fa-github"></i> Github</a>'
    }
}


class User(BaseUser):
    type = 'oauth'
    provider = None

    def __init__(self, provider, username, token):
        self.provider = provider
        self.username = username
        self.id = username
        self.token = token

    @property
    def auth_token_id(self):
        return self.token

    @staticmethod
    def load_user(*args, **kwargs):
        return User.get_by_id(args[0])

    @staticmethod
    def get_by_id(user_id):
        return users.get(user_id)

    @staticmethod
    def auth(username, provider, token):
        user = User(provider, username, User.hash_password(token))
        users[user.id] = user
        if user:
            login_user(user, remember=True)
            return True
        else:
            return False

    @classmethod
    def get_app(cls, provider):
        if oauth.remote_apps.get(provider):
            return oauth.remote_apps.get(provider)
        return oauth.remote_app(
            provider,
            consumer_key=config.OAUTH.get(provider, {}).get('key'),
            consumer_secret=config.OAUTH.get(provider, {}).get(
                'secret'),
            **providers[provider]['oauth'])

    def get_id(self):
        return unicode("%s/%s/%s" % (self.type, self.provider, self.id))

    @staticmethod
    def login_form():
        buttons = []
        for k, v in providers.items():
            buttons.append(v.get('button'))

        return " ".join(buttons)
