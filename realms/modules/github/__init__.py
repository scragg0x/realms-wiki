from realms import login_manager, github
from flask import request, flash, redirect, g
from flask.ext.login import login_url


@login_manager.unauthorized_handler
def unauthorized():
    if request.method == 'GET':
        flash('Please log in to access this page')
        return redirect(login_url('github.login', request.url))
    else:
        return dict(error=True, message="Please log in for access."), 403


@github.access_token_getter
def github_token_getter():
    # A workaround, put the oauth token in Flask global for now, because
    # github-flask accesses it this way.
    return g.get('github_access_token', None)
