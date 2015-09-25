from flask import (
    current_app, render_template, redirect, Blueprint, flash, url_for, g
)
from flask.ext.github import GitHubError
from flask.ext.login import login_user, logout_user
from realms import github
from realms.modules.github.models import User

blueprint = Blueprint('github', __name__)


@blueprint.route("/login")
def login():
    return render_template("github/login.html")


@blueprint.route("/github/authorize")
def authorize():
    """
    Redirect user to Github to authorize
    """
    BASE_URL = current_app.config['BASE_URL']
    redirect_uri = '{}{}'.format(BASE_URL, url_for('github.authorized'))

    return github.authorize(
        scope='user:email,read:org',
        redirect_uri=redirect_uri
    )


@blueprint.route('/github/callback')
@github.authorized_handler
def authorized(oauth_token):
    """
    Callback from Github, will call with a oauth_token
    """
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(url_for(current_app.config['ROOT_ENDPOINT']))

    g.github_access_token = oauth_token

    github_user = github.get('user')

    emails = github.get('user/emails')

    # Get the primary email
    email = None
    for e in emails:
        if e['primary']:
            email = e['email']
            break

    username = github_user['login']

    # Check membership of organization
    # TODO add GITHUB_AUTHORIZED_USERNAMES or something
    org = current_app.config['GITHUB_AUTHORIZED_ORG']
    membership_url = 'orgs/{}/members/{}'.format(org, username)
    try:
        github.get(membership_url)
    except GitHubError:
        flash('Not org member')
    else:
        user = User(username, email=email)
        login_user(user, remember=True)

    return redirect(url_for(current_app.config['ROOT_ENDPOINT']))


@blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for(current_app.config['ROOT_ENDPOINT']))
