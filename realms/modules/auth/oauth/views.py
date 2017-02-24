from __future__ import absolute_import

from flask import Blueprint, url_for, request, flash, redirect, session, current_app
from .models import User
from realms import config

blueprint = Blueprint('auth.oauth', __name__)
config = config.conf


def oauth_failed(next_url):
    flash('You denied the request to sign in.')
    return redirect(next_url)


@blueprint.route("/login/oauth/<provider>")
def login(provider):
    return User.get_app(provider).authorize(callback=url_for('auth.oauth.callback', provider=provider, _external=True))


@blueprint.route('/login/oauth/<provider>/callback')
def callback(provider):
    next_url = session.get('next_url') or url_for(current_app.config['ROOT_ENDPOINT'])
    try:
        remote_app = User.get_app(provider)
        resp = remote_app.authorized_response()
        if resp is None:
            flash('You denied the request to sign in.', 'error')
            flash('Reason: ' + request.args['error_reason'] +
                  ' ' + request.args['error_description'], 'error')
            return redirect(next_url)
    except Exception as e:
        flash('Access denied: %s' % e.message)
        return redirect(next_url)

    oauth_token = resp.get(User.get_provider_value(provider, 'token_name'))
    session[provider + "_token"] = (oauth_token, '')
    profile = User.get_provider_value(provider, 'profile')
    data = remote_app.get(profile).data if profile else resp

    # Adding check to verify domain restriction this is hacky but works.
    # A proper implementation should be in flask_oauthlib but its not there
    # so we do it a hacky way like this

    restricted_domain = config.OAUTH.get(provider, {}).get('domain', None)

    # If the domain restriction is in place then we verify the domain
    # provided in config and oauth and check if both are some,
    # if not same we do not authenticate in our system
    if restricted_domain:
        if data['hd'] == restricted_domain:
            User.auth(provider, data, oauth_token)
            return redirect(next_url)
        else:
            flash('You are not authorized to sign in.', 'error')
            flash('Reason: Domain restriction in place, domain:"%s" is not allowed to sign in' % data['hd'])
            return redirect(next_url)
    # If no domain restriction is in place, just authenticate
    # user and create user
    else:
        User.auth(provider, data, oauth_token)
        return redirect(next_url)
