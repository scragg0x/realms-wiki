from flask import Blueprint, url_for, request, flash, redirect
from .models import TwitterUser

blueprint = Blueprint('auth.oauth', __name__)


def oauth_failed(next_url):
    flash(u'You denied the request to sign in.')
    return redirect(next_url)

@blueprint.route("/login/twitter")
def login_twitter():
    return TwitterUser.app.authorize(callback=url_for('twitter_callback',
                                                      next=request.args.get('next') or request.referrer or None))

@blueprint.route('/login/twitter/callback')
def twitter_callback():
    next_url = request.args.get('next') or url_for('index')
    resp = TwitterUser.app.authorized_response()
    if resp is None:
        return oauth_failed(next_url)

    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    session['twitter_user'] = resp['screen_name']

    flash('You were signed in as %s' % resp['screen_name'])
    return redirect(next_url)