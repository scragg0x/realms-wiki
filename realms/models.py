import bcrypt
from sqlalchemy import Column, Integer, String, Time
from flask import session, flash
from flask.ext.login import login_user, logout_user
from realms.lib.services import db
from realms.lib.util import gravatar_url, to_dict


class ModelMixin(object):
    def __getitem__(self, k):
        return self.__getattribute__(k)

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj


class CurrentUser():
    id = None

    def __init__(self, id):
        self.id = id
        if id:
            session['user'] = to_dict(User.query.filter_by(id=id).first())

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


class Site(ModelMixin, db.Model):
    __tablename__ = 'sites'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    pages = Column(Integer)
    views = Column(Integer)
    founder = Column(Integer)
    created_at = Column(Time)
    updated_at = Column(Time)

    @classmethod
    def get_by_name(cls, name):
        return Site.query.filter_by(name=name).first()


class User(db.Model, ModelMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    email = Column(String(255))
    avatar = Column(String(255))
    password = Column(String(255))
    created_at = Column(Time)
    updated_at = Column(Time)

    @classmethod
    def get_by_email(cls, email):
        return User.query.filter_by(email=email).first()

    @classmethod
    def get_by_username(cls, username):
        return User.query.filter_by(username=username).first()

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
    def login(cls, id):
        login_user(CurrentUser(id), remember=True)

    @classmethod
    def logout(cls):
        logout_user()
        session.pop('user', None)