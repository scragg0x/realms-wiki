from flask.ext.login import UserMixin, logout_user, login_user, AnonymousUserMixin
from realms import config, login_manager, db
from realms.lib.model import Model
from realms.lib.util import gravatar_url
from itsdangerous import URLSafeSerializer, BadSignature
from hashlib import sha256
import bcrypt


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@login_manager.token_loader
def load_token(token):
    # Load unsafe because payload is needed for sig
    sig_okay, payload = URLSafeSerializer(config.SECRET_KEY).loads_unsafe(token)

    if not payload:
        return None

    # User key *could* be stored in payload to avoid user lookup in db
    user = User.get_by_id(payload.get('id'))

    if not user:
        return None

    try:
        if User.signer(sha256(user.password).hexdigest()).loads(token):
            return user
        else:
            return None
    except BadSignature:
        return None


class AnonUser(AnonymousUserMixin):
    username = 'Anon'
    email = ''
    admin = False


class User(Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    admin = False

    hidden_fields = ['password']
    readonly_fields = ['email', 'password']

    def get_auth_token(self):
        key = sha256(self.password).hexdigest()
        return User.signer(key).dumps(dict(id=self.id))

    @property
    def avatar(self):
        return gravatar_url(self.email)

    @staticmethod
    def create(username, email, password):
        u = User()
        u.username = username
        u.email = email
        u.password = User.hash_password(password)
        u.save()

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def signer(salt):
        """
        Signed with app secret salted with sha256 of password hash of user (client secret)
        """
        return URLSafeSerializer(config.SECRET_KEY + salt)

    @staticmethod
    def auth(email, password):
        user = User.query.filter_by(email=email).first()

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

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))

    @staticmethod
    def check_password(password, hashed):
        return bcrypt.hashpw(password.encode('utf-8'), hashed.encode('utf-8')) == hashed

    @classmethod
    def logout(cls):
        logout_user()

login_manager.anonymous_user = AnonUser