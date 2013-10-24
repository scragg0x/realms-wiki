import json
import rethinkdb as rdb
import bcrypt
from flask import session, flash
from flask.ext.login import login_user, logout_user
from util import gravatar_url
from services import db, cache


def to_json(res, first=False):
    """
    Jsonify query result.
    """
    res = to_dict(res, first)
    return json.dumps(res, separators=(',',':'))


def to_dict(cur, first=False):
    if not cur:
        return None
    ret = []
    for row in cur:
        ret.append(row)
    if ret and first:
        return ret[0]
    else:
        return ret


def cache_it(fn):
    def wrap(*args, **kw):
        key = "%s:%s" % (args[0].table, args[1])
        data = cache.get(key)
        # Assume strings are JSON encoded
        try:
            data = json.loads(data)
        except TypeError:
            pass
        except ValueError:
            pass

        if data is not None:
            return data
        else:
            data = fn(*args)
            print data
            ret = data
            if data is None:
                data = ''
            if not isinstance(data, basestring):
                try:
                    data = json.dumps(data, separators=(',', ':'))
                except TypeError:
                    pass
            cache.set(key, data)
            return ret
    return wrap


class BaseModel():

    table = None
    _conn = db

    def __init__(self, **kwargs):
        if not kwargs.get('conn'):
            kwargs['conn'] = db

    def create(self, **kwargs):
        return rdb.table(self.table).insert(kwargs).run(self._conn)

    @cache_it
    def get_by_id(self, id):
        return rdb.table(self.table).get(id).run(self._conn)

    def get_all(self, arg, index):
        return rdb.table(self.table).get_all(arg, index=index).run(self._conn)

    #@cache_it
    def get_one(self, arg, index):
        return rdb.table(self.table).get_all(arg, index=index).limit(1).run(self._conn)


class Site(BaseModel):
    table = 'sites'

    def get_by_name(self, name):
        return to_dict(self.get_one(name, 'name'), True)


class CurrentUser():
    id = None

    def __init__(self, id):
        self.id = id
        if id:
            user = User()
            session['user'] = user.get_by_id(id)

    def get_id(self):
        return self.id

    def is_active(self):
        return True if self.id else False

    def is_anonymous(self):
        return False if self.id else True

    def is_authenticated(self):
        return True if self.id else False

    @staticmethod
    def get(key):
        try:
            return session['user'][key]
        except KeyError:
            return None


class User(BaseModel):
    table = 'users'

    def get_by_email(self, email):
        return to_dict(self.get_one(email, 'email'), True)

    def get_by_username(self, username):
        return to_dict(self.get_one(username, 'username'), True)

    def login(self, login, password):
        pass

    @classmethod
    def auth(cls, username, password):
        u = User()
        data = u.get_by_email(username)
        if not data:
            return False

        if bcrypt.checkpw(password, data['password']):
            cls.login(data['id'])
            return True
        else:
            return False

    @classmethod
    def register(cls, username, email, password):
        user = User()
        email = email.lower()
        if user.get_by_email(email):
            flash('Email is already taken')
            return False
        if user.get_by_username(username):
            flash('Username is already taken')
            return False

        # Create user and login
        u = User.create(email=email,
                        username=username,
                        password=bcrypt.hashpw(password, bcrypt.gensalt(10)),
                        avatar=gravatar_url(email))

        User.login(u.id)

    @classmethod
    def login(cls, id, data=None):
        login_user(CurrentUser(id), True)

    @classmethod
    def logout(cls):
        logout_user()
        session.pop('user', None)