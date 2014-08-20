from flask.ext.login import UserMixin, logout_user, login_user
from realms import config, login_manager
from realms.lib.services import db
from itsdangerous import URLSafeSerializer, BadSignature
from hashlib import sha256
import json
import bcrypt

FIELD_MAP = dict(
    u='username',
    e='email',
    p='password',
    nv='not_verified',
    a='admin',
    b='banned')


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@login_manager.token_loader
def load_token(token):
    # Load unsafe because payload is needed for sig
    sig_okay, payload = URLSafeSerializer(None).load_unsafe(token)

    if not payload:
        return False

    # User key *could* be stored in payload to avoid user lookup in db
    user = User.get(payload.get('id'))

    if not user:
        return False

    try:
        if User.signer(sha256(user.password).hexdigest()).loads(token):
            return user
        else:
            return False
    except BadSignature:
        return False


class User(UserMixin):

    username = None
    email = None
    password = None

    def __init__(self, email, data=None):
        self.id = email
        for k, v in data.items():
            setattr(self, FIELD_MAP.get(k, k), v)

    def get_auth_token(self):
        key = sha256(self.password).hexdigest()
        return User.signer(key).dumps(dict(id=self.username))

    @staticmethod
    def create(username, email, password):
        User.set(email, dict(u=username, e=email, p=User.hash(password), nv=1))

    @staticmethod
    def signer(salt):
        """
        Signed with app secret salted with sha256 of password hash of user (client secret)
        """
        return URLSafeSerializer(config.SECRET + salt)

    @staticmethod
    def set(email, data):
        db.set('u:%s' % email, json.dumps(data, separators=(',', ':')))

    @staticmethod
    def get(email):
        data = db.get('u:%s', email)

        try:
            data = json.loads(data)
        except ValueError:
            return None

        if data:
            return User(email, data)
        else:
            return None

    @staticmethod
    def auth(email, password):
        user = User.get(email)

        if not user:
            return False

        if bcrypt.checkpw(password, user.password):
            login_user(user, remember=True)
            return user
        else:
            return False

    @staticmethod
    def hash(password):
        return bcrypt.hashpw(password, bcrypt.gensalt(log_rounds=12))

    @classmethod
    def logout(cls):
        logout_user()

