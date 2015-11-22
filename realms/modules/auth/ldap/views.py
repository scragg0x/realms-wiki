from flask import current_app, request, redirect, Blueprint, flash, url_for
from ..ldap.models import User
from flask_ldap_login import LDAPLoginForm

blueprint = Blueprint('auth.ldap', __name__)


@blueprint.route("/login/ldap", methods=['POST'])
def login():
    form = LDAPLoginForm()

    if not form.validate():
        flash('Form invalid', 'warning')
        return redirect(url_for('auth.login'))

    if User.auth(form.user, request.form['password']):
        return redirect(request.args.get("next") or url_for(current_app.config['ROOT_ENDPOINT']))
    else:
        return redirect(url_for('auth.login'))
