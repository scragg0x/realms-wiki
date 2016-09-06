from __future__ import absolute_import

from flask import current_app, request, redirect, Blueprint, flash, url_for, session

from .models import User
from .forms import LoginForm


blueprint = Blueprint('auth.ldap', __name__)


@blueprint.route("/login/ldap", methods=['POST'])
def login():
    form = LoginForm()

    if not form.validate():
        flash('Form invalid', 'warning')
        return redirect(url_for('auth.login'))

    if User.auth(request.form['username'], request.form['password']):
        return redirect(request.args.get('next') or url_for(current_app.config['ROOT_ENDPOINT']))
    else:
        flash('User ID or password is incorrect', 'warning')
        return redirect(url_for('auth.login'))
