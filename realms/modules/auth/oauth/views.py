from flask import Blueprint, url_for, request, flash, redirect, session, current_app
from .models import User

blueprint = Blueprint('auth.oauth', __name__)


def oauth_failed(next_url):
    flash('You denied the request to sign in.')
    return redirect(next_url)


@blueprint.route("/login/oauth/<provider>")
def login(provider):
    return User.get_app(provider).authorize(callback=url_for('auth.oauth.callback', provider=provider, _external=True))


@blueprint.route('/login/oauth/<provider>/callback')
def callback(provider):
    next_url = request.args.get('next') or url_for(current_app.config['ROOT_ENDPOINT'])
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

    User.auth(provider, data, oauth_token)

    return redirect(next_url)
