from flask import render_template
from flask_oauthlib.client import OAuth
from realms import config
from ..models import BaseUser

oauth = OAuth()


class OAuthUser(BaseUser):
    # OAuth remote app
    app = None


class TwitterUser(OAuthUser):

    app = oauth.remote_app(
        'twitter',
        base_url='https://api.twitter.com/1/',
        request_token_url='https://api.twitter.com/oauth/request_token',
        access_token_url='https://api.twitter.com/oauth/access_token',
        authorize_url='https://api.twitter.com/oauth/authenticate',
        consumer_key=config.TWITTER_KEY,
        consumer_secret=config.TWITTER_SECRET)

    def __init__(self, id_, username, email=None):
        self.id = id_
        self.username = username
        self.email = email

    @staticmethod
    def load_user(*args, **kwargs):
        return TwitterUser(args[0])

    @staticmethod
    def login_form():
        return render_template('auth/oauth/twitter.html')
