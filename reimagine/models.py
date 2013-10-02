import rethinkdb as rdb
from reimagine import conn
from rethinkORM import RethinkModel


class BaseModel(RethinkModel):

    def __init__(self, **kwargs):
        if not kwargs.get('conn'):
            kwargs['conn'] = conn

        super(BaseModel, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        return super(BaseModel, cls).create(**kwargs)


class Site(BaseModel):
    table = 'sites'


class User(BaseModel):
    table = 'users'


    def login(self, login, password):
        pass