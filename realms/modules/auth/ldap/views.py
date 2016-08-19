<<<<<<< HEAD
from flask import current_app, request, redirect, Blueprint, flash, url_for, session
from ..ldap.models import User
=======
from __future__ import absolute_import

from flask import current_app, request, redirect, Blueprint, flash, url_for
>>>>>>> systematic use of `from __future__ import absolute_import`. it eliminates `import NAME` confusion with very common names (eg. `import ldap` is very ambiguous: can be a ldap module from realms-wiki, a ldap module from flask-ldap-login, or `python-ldap` module.
from flask_ldap_login import LDAPLoginForm

from .models import User

blueprint = Blueprint('auth.ldap', __name__)


@blueprint.route("/login/ldap", methods=['POST'])
def login():
    form = LDAPLoginForm()

    if not form.validate():
        flash('Form invalid', 'warning')
        return redirect(url_for('auth.login'))

    if User.auth(form.user, request.form['password']):
        return redirect(session.get("next_url") or url_for(current_app.config['ROOT_ENDPOINT']))
    else:
        return redirect(url_for('auth.login'))
