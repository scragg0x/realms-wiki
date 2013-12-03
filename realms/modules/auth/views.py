from flask import render_template, redirect, request, url_for, flash, Blueprint
from realms import redirect_url
from realms.models import User

blueprint = Blueprint('auth', __name__)


@blueprint.route("/logout/")
def logout():
    User.logout()
    return redirect(url_for('root'))


@blueprint.route("/register/", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.register(request.form.get('username'), request.form.get('email'), request.form.get('password')):
            return redirect(url_for('root'))
        else:
            # Login failed
            return redirect(url_for('.register'))
    else:
        return render_template('auth/register.html')


@blueprint.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if User.auth(request.form['email'], request.form['password']):
            return redirect(redirect_url(referrer=url_for('root')))
        else:
            flash("Email or Password invalid")
            return redirect(url_for(".login"))
    else:
        return render_template('auth/login.html')