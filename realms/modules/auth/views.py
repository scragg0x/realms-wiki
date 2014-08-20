from flask import g, render_template, request, redirect, Blueprint, flash, url_for
from realms.modules.auth.models import User
from realms.modules.auth.forms import LoginForm, RegistrationForm
from realms import config

blueprint = Blueprint('auth', __name__, url_prefix=config.RELATIVE_PATH)


@blueprint.route("/logout")
def logout_page():
    User.logout()
    flash("You are now logged out")
    return redirect(url_for(config.ROOT_ENDPOINT))


@blueprint.route("/login")
def login():
    if request.method == "POST":
        form = RegistrationForm()

        # TODO
        if not form.validate():
            flash('Form invalid')
            return redirect(url_for('auth.login'))

        if User.auth(request.form['email'], request.form['password']):
            return redirect(request.args.get("next") or url_for(config.ROOT_ENDPOINT))

    return render_template("auth/login.html")

@blueprint.route("/register")
def register():
    if request.method == "POST":
        return redirect(request.args.get("next") or url_for(config.ROOT_ENDPOINT))
    else:
        return render_template("auth/register.html")