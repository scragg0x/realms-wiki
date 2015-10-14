from flask import current_app, render_template, request, redirect, Blueprint, flash, url_for
from flask.ext.login import logout_user
from realms.modules.auth.models import Auth

blueprint = Blueprint('auth', __name__)


@blueprint.route("/login", methods=['GET', 'POST'])
def login():
    return render_template("auth/login.html", forms=Auth.login_forms())


@blueprint.route("/logout")
def logout():
    logout_user()
    flash("You are now logged out")
    return redirect(url_for(current_app.config['ROOT_ENDPOINT']))


@blueprint.route("/settings", methods=['GET', 'POST'])
def settings():
    return render_template("auth/settings.html")
