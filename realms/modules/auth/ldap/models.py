from flask import current_app, render_template
from flask.ext.login import login_user
from realms import ldap
from flask_ldap_login import LDAPLoginForm
from ..models import BaseUser
import bcrypt

users = {}

@ldap.save_user
def save_user(username, userdata):
    users[username] = User(username, userdata)
    return users[username]

class User(BaseUser):
    type = 'ldap'

    def __init__(self, username, data):
        self.id = username
        self.username = username
        self.data = data

    @staticmethod
    def login_form():
        form = LDAPLoginForm()
        return render_template('auth/ldap/login.html', form=form)

    @staticmethod
    def auth(*args):
        login_user(args[0].user, remember=True)
        return True
