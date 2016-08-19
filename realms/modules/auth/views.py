from __future__ import absolute_import

from flask import current_app, render_template, request, redirect, Blueprint, flash, url_for, session
from flask_login import logout_user

from realms.modules.auth.models import Auth


blueprint = Blueprint('auth', __name__, template_folder='templates')


@blueprint.route("/login", methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or url_for(current_app.config['ROOT_ENDPOINT'])
    session['next_url'] = next_url
    return render_template("auth/login.html", forms=Auth.login_forms())


@blueprint.route("/logout")
def logout():
    logout_user()
    flash("You are now logged out")
    return redirect(url_for(current_app.config['ROOT_ENDPOINT']))


@blueprint.route("/settings", methods=['GET', 'POST'])
def settings():
    return render_template("auth/settings.html")
