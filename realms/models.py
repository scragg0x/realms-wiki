import bcrypt
from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base
from flask import session, flash
from flask.ext.login import login_user, logout_user
from realms.lib.util import gravatar_url, to_dict
from realms.lib.services import db

Base = declarative_base()


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


class Site(Base):
    __tablename__ = 'sites'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    pages = Column(Integer)
    views = Column(Integer)
    created = Column(Time)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    email = Column(String(255))
    password = Column(String(255))
    joined = Column(Time)

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
    def login(cls, id):
        login_user(CurrentUser(id), True)

    @classmethod
    def logout(cls):
        logout_user()
        session.pop('user', None)