from flask import current_app, render_template
from flask.ext.login import logout_user, login_user
from realms import login_manager, db
from realms.lib.model import Model
from ..models import BaseUser
from .forms import LoginForm
from itsdangerous import URLSafeSerializer, BadSignature
from hashlib import sha256


@login_manager.token_loader
def load_token(token):
    # Load unsafe because payload is needed for sig
    sig_okay, payload = URLSafeSerializer(current_app.config['SECRET_KEY']).loads_unsafe(token)

    if not payload:
        return None

    # User key *could* be stored in payload to avoid user lookup in db
    user = User.get_by_id(payload.get('id'))

    if not user:
        return None

    try:
        if BaseUser.signer(sha256(user.password).hexdigest()).loads(token):
            return user
        else:
            return None
    except BadSignature:
        return None


class User(Model, BaseUser):
    __tablename__ = 'users'
    type = 'local'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(60))
    admin = False

    hidden_fields = ['password']
    readonly_fields = ['email', 'password']

    @property
    def auth_token_id(self):
        return self.password

    @staticmethod
    def load_user(*args, **kwargs):
        return User.get_by_id(args[0])

    @staticmethod
    def create(username, email, password):
        u = User()
        u.username = username
        u.email = email
        u.password = User.hash_password(password)
        u.save()

    @staticmethod
    def get_by_username(username):
        return User.query().filter_by(username=username).first()

    @staticmethod
    def get_by_email(email):
        return User.query().filter_by(email=email).first()

    @staticmethod
    def signer(salt):
        return URLSafeSerializer(current_app.config['SECRET_KEY'] + salt)

    @staticmethod
    def auth(email, password):
        user = User.get_by_email(email)

        if not user:
            # User doesn't exist
            return False

        if User.check_password(password, user.password):
            # Password is good, log in user
            login_user(user, remember=True)
            return user
        else:
            # Password check failed
            return False

    @classmethod
    def logout(cls):
        logout_user()

    @staticmethod
    def login_form():
        form = LoginForm()
        return render_template('auth/local/login.html', form=form)

