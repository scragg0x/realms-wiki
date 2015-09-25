from flask.ext.login import UserMixin, AnonymousUserMixin
from realms import login_manager
from realms.lib.util import gravatar_url


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


class AnonUser(AnonymousUserMixin):
    username = 'Anon'
    email = ''


class User(UserMixin):
    def __init__(self, username, email='test@test.com'):
        self.username = username
        self.email = email

    @property
    def id(self):
        return self.username

    @property
    def avatar(self):
        return gravatar_url(self.email)


login_manager.anonymous_user = AnonUser
