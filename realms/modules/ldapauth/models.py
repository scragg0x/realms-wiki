from flask import current_app
from flask.ext.login import UserMixin, logout_user, login_user, AnonymousUserMixin
from realms import login_manager
from realms.lib.util import gravatar_url
from itsdangerous import URLSafeSerializer, BadSignature
from hashlib import sha256
import ldap
import bcrypt


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@login_manager.token_loader
def load_token(token):
    # Load unsafe because payload is needed for sig
    sig_okay, payload = URLSafeSerializer(current_app.config['SECRET_KEY']).loads_unsafe(token)

    if not payload:
        return None

    user = User.get_by_id(payload.get('id'))

    if not user:
        return None

    try:
        if User.signer(sha256(user.dn).hexdigest()).loads(token):
            return user
        else:
            return None
    except BadSignature:
        return None
    

class AnonUser(AnonymousUserMixin):
    username = 'Anon'
    email = ''
    admin = False


class User(UserMixin):

    def __init__(self, dn, entry):
        self.dn = dn
        self.username = entry['uid'][0]
        self.fullname = entry['cn'][0]
        self.email = entry['mail'][0]

    def get_id(self):
        return unicode(self.email)

    def get_auth_token(self):
        return User.signer(self.dn).dumps(dict(id=self.get_id()))

    @property
    def avatar(self):
        return gravatar_url(self.email)

    @staticmethod
    def simple_search(query):
        ld = ldap.initialize(current_app.config['LDAP_URI'])
        
        v = ld.search_s(current_app.config['LDAP_BASE'],
                        ldap.SCOPE_SUBTREE, query, None)
        if v:
            return User(v[0][0], v[0][1])

        return None
    
    @staticmethod
    def get_by_id(id):
        return User.simple_search('mail=%s' % id)
    
    @staticmethod
    def get_by_username(username):
        return User.simple_search('uid=%s' % username)

    @staticmethod
    def get_by_email(email):
        return User.simple_search('mail=%s' % email)

    @staticmethod
    def signer(salt):
        return URLSafeSerializer(current_app.config['SECRET_KEY'] + salt)

    @staticmethod
    def auth(email, password):
        # We do a search first to get the dn. Doing the bind first
        # would avoid the anonymous lookup,
        # but then we'd have to construct the uid
        # from the email address, which involves assumptions
        # Also, we need anonymous lookups anyway for load_user
        ld = ldap.initialize(current_app.config['LDAP_URI'])
        v = ld.search_s(current_app.config['LDAP_BASE'],
                        ldap.SCOPE_SUBTREE, 'mail=%s' % email, None)

        if v is None:
            return False
        
        user = User(v[0][0], v[0][1])
        try:
            ld.bind_s(user.dn, password)
            login_user(user, remember=True)
            user.hashpw = bcrypt.hashpw(password.encode('utf-8'),
                                        bcrypt.gensalt(12))
            return user
        except ldap.INVALID_CREDENTIALS:
            return False

    @classmethod
    def logout(cls):
        logout_user()
        
login_manager.anonymous_user = AnonUser
