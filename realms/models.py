import rethinkdb as rdb
from flask import session
from flask.ext.login import login_user
from rethinkORM import RethinkModel
from realms import conn, bcrypt


def to_dict(cur, first=False):
    ret = []
    for row in cur:
        ret.append(row)
    if ret and first:
        return ret[0]
    else:
        return ret


class BaseModel(RethinkModel):

    def __init__(self, **kwargs):
        if not kwargs.get('conn'):
            kwargs['conn'] = conn
        super(BaseModel, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        return super(BaseModel, cls).create(**kwargs)

    def get_all(self, arg, index):
        return rdb.table(self.table).get_all(arg, index=index).run(self._conn)

    def get_one(self, arg, index):
        return rdb.table(self.table).get_all(arg, index=index).limit(1).run(self._conn)


class Site(BaseModel):
    table = 'sites'


class CurrentUser():
    id = None

    def __init__(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False if self.id else True

    def is_authenticated(self):
        return True if self.id else False


class User(BaseModel):
    table = 'users'

    def get_by_email(self, email):
        return to_dict(self.get_one(email, 'email'), True)

    def get_by_username(self, username):
        return to_dict(self.get_one(username, 'username'), True)

    def login(self, login, password):
        pass

    @classmethod
    def get(cls, id):
        print id
        return cls(id=id)

    @classmethod
    def auth(cls, username, password):
        u = User()
        data = u.get_by_email(username)
        if not data:
            return False

        if bcrypt.check_password_hash(data['password'], password):
            login_user(CurrentUser(data['id']))
            session['user'] = data
            return True
        else:
            return False