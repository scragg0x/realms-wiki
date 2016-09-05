from __future__ import absolute_import

from flask import current_app, render_template, request, redirect, Blueprint, flash, url_for, session

from .models import User
from .forms import LoginForm, RegistrationForm


blueprint = Blueprint('auth.local', __name__)


@blueprint.route("/login/local", methods=['POST'])
def login():
    form = LoginForm()

    if not form.validate():
        flash('Form invalid', 'warning')
        return redirect(url_for('auth.login'))

    if User.auth(request.form['email'], request.form['password']):
        return redirect(request.args.get("next") or url_for(current_app.config['ROOT_ENDPOINT']))
    else:
        flash('Email or Password Incorrect', 'warning')
        return redirect(url_for('auth.login'))


@blueprint.route("/register", methods=['GET', 'POST'])
def register():

    if not current_app.config['REGISTRATION_ENABLED']:
        flash("Registration is disabled")
        return redirect(url_for(current_app.config['ROOT_ENDPOINT']))

    form = RegistrationForm()

    if request.method == "POST":

        if not form.validate():
            flash('Form invalid', 'warning')
            return redirect(url_for('auth.local.register'))

        if User.get_by_username(request.form['username']):
            flash('Username is taken', 'warning')
            return redirect(url_for('auth.local.register'))

        if User.get_by_email(request.form['email']):
            flash('Email is taken', 'warning')
            return redirect(url_for('auth.local.register'))

        User.create(request.form['username'], request.form['email'], request.form['password'])
        User.auth(request.form['email'], request.form['password'])

        return redirect(session.get("next_url") or url_for(current_app.config['ROOT_ENDPOINT']))

    return render_template("auth/register.html", form=form)
