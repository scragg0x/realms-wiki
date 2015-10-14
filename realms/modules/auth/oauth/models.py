from flask import render_template
from flask_oauthlib.client import OAuth
from realms import config
from ..models import BaseUser

oauth = OAuth()


class OAuthUser(BaseUser):
    # OAuth remote app
    remote_app = None


class TwitterUser(OAuthUser):

    def __init__(self, id_, username, email=None):
        self.id = id_
        self.username = username
        self.email = email

    @classmethod
    def app(cls):
        if cls.remote_app:
            return cls.remote_app

        cls.remote_app = oauth.remote_app(
            'twitter',
            base_url='https://api.twitter.com/1/',
            request_token_url='https://api.twitter.com/oauth/request_token',
            access_token_url='https://api.twitter.com/oauth/access_token',
            authorize_url='https://api.twitter.com/oauth/authenticate',
            consumer_key=config.OAUTH['twitter']['key'],
            consumer_secret=config.OAUTH['twitter']['secret'])
        return cls.remote_app

    @staticmethod
    def load_user(*args, **kwargs):
        return TwitterUser(args[0])

    @staticmethod
    def login_form():
        return render_template('auth/oauth/twitter.html')
