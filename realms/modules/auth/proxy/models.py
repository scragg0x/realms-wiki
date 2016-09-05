from __future__ import absolute_import

from flask_login import login_user

from realms.modules.auth.models import BaseUser


users = {}


class User(BaseUser):
    type = 'proxy'

    def __init__(self, username, email='null@localhost.local', password="dummypassword"):
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
        return None

    @staticmethod
    def do_login(user_id):
        user = User(user_id)
        users[user_id] = user
        login_user(user, remember=True)
        return True

