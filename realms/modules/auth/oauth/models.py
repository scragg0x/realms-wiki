from flask import render_template
from flask_oauthlib.client import OAuth
from realms import config
from ..models import BaseUser

oauth = OAuth()

users = {}

providers = {
    'twitter': {
        'oauth': dict(
            base_url='https://api.twitter.com/1/',
            request_token_url='https://api.twitter.com/oauth/request_token',
            access_token_url='https://api.twitter.com/oauth/access_token',
            authorize_url='https://api.twitter.com/oauth/authenticate')
    }
}


class User(BaseUser):

    @classmethod
    def get_app(cls, provider):
        return oauth.remote_app(provider,
                                consumer_key=config.OAUTH.get(provider, {}).get('key'),
                                consumer_secret=config.OAUTH.get(provider, {}).get('secret'),
                                **providers[provider]['oauth'])

    @staticmethod
    def login_form():
        pass
