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
        'button': '<a href="/login/oauth/twitter" class="btn btn-default"><i class="fa fa-twitter"></i> Twitter</a>',
        'field_map': {
            'id': 'user_id',
            'username': 'screen_name'
        }
    },
    'github': {
        'oauth': dict(
            request_token_params={'scope': 'user:email'},
            base_url='https://api.github.com/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize'),
        'button': '<a href="/login/oauth/github" class="btn btn-default"><i class="fa fa-github"></i> Github</a>',
        'field_map': {
            'id': ['user', 'id'],
            'username': ['user', 'login'],
            'email': ['user', 'email']
        }
    },
    'facebook': {
        'oauth': dict(
            request_token_params={'scope': 'email'},
            base_url='https://graph.facebook.com',
            request_token_url=None,
            access_token_url='/oauth/access_token',
            access_token_method='GET',
            authorize_url='https://www.facebook.com/dialog/oauth'
        ),
        'button': '<a href="/login/oauth/facebook" class="btn btn-default"><i class="fa fa-facebook"></i> Facebook</a>',
        'field_map': {
            'id': 'id',
            'username': 'name',
            'email': 'email'
        }
    },
    'google': {
        'oauth': dict(
            request_token_params={
                'scope': 'https://www.googleapis.com/auth/userinfo.email'
            },
            base_url='https://www.googleapis.com/oauth2/v1/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            authorize_url='https://accounts.google.com/o/oauth2/auth',
        ),
        'button': '<a href="/login/oauth/google" class="btn btn-default"><i class="fa fa-google"></i> Google</a>'
    }
}


class User(BaseUser):
    type = 'oauth'
    provider = None

    def __init__(self, provider, user_id, username, token):
        self.provider = provider
        self.username = username
        self.id = user_id
        self.token = token
        self.auth_id = "%s-%s" % (provider, username)

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
    def auth(provider, resp):
        field_map = providers.get(provider).get('field_map')
        if not field_map:
            raise NotImplementedError

        def get_value(d, key):
            if isinstance(key, basestring):
                return d.get(key)
            # key should be list here
            val = d.get(key.pop(0))
            if len(key) == 0:
                # if empty we have our value
                return val
            # keep digging
            return get_value(val, key)

        fields = {}
        for k, v in field_map.items():
            fields[k] = get_value(resp, v)

        user = User(provider, fields['id'], fields['username'], User.hash_password(resp['oauth_token']))
        users[user.auth_id] = user

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
        return unicode("%s/%s" % (self.type, self.auth_id))

    @staticmethod
    def login_form():
        buttons = []
        for name, val in providers.items():
            if not config.OAUTH.get(name, {}).get('key') or not config.OAUTH.get(name, {}).get('secret'):
                continue
            buttons.append(val.get('button'))

        return "<h4>Social Login</h4>" + " ".join(buttons)
