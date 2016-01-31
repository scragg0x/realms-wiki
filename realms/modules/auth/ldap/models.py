from flask import render_template
from flask.ext.login import login_user
from realms import ldap
from flask_ldap_login import LDAPLoginForm
from ..models import BaseUser


users = {}


@ldap.save_user
def save_user(username, userdata):
    user = User(username, userdata.get('email'))
    users[user.id] = user
    return user


class User(BaseUser):
    type = 'ldap'

    def __init__(self, username, email='null@localhost.local', password=None):
        self.id = username
        self.username = username
        self.email = email
        self.password = password

    @property
    def auth_token_id(self):
        return self.password

    @staticmethod
    def load_user(*args, **kwargs):
        return User.get_by_id(args[0])

    @staticmethod
    def get_by_id(user_id):
        return users.get(user_id)

    @staticmethod
    def login_form():
        return render_template('auth/ldap/login.html', form=LDAPLoginForm())

    @staticmethod
    def auth(user, password):
        password = User.hash_password(password)
        user.password = password
        users[user.id] = user
        if user:
            login_user(user, remember=True)
            return True
        else:
            return False

