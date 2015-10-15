from flask import Blueprint, url_for, request, flash, redirect, session
from .models import User

blueprint = Blueprint('auth.oauth', __name__)


def oauth_failed(next_url):
    flash('You denied the request to sign in.')
    return redirect(next_url)


@blueprint.route("/login/oauth/<provider>")
def oauth_login(provider):
    return User.get_app(provider).authorize(callback=url_for('oauth_callback', provider=provider,
        next=request.args.get('next') or request.referrer or None))


@blueprint.route('/login/oauth/<provider>/callback')
def oauth_callback(provider):
    next_url = request.args.get('next') or url_for('index')
    resp = User.get_app(provider).authorized_response()
    if resp is None:
        return oauth_failed(next_url)

    session[provider + '_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )

    return redirect(next_url)
