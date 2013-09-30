import rethinkdb as rdb
from reimagine import conn


def get_one(cur):
    res = cur.chunks[0]
    return res[0] if len(res) else None


class BaseModel():
    __table__ = None
    _conn = conn

    def __init__(self):
        pass

    @classmethod
    def filter(cls, f, limit=None):
        q = rdb.table(cls.__table__).filter(f)
        if limit:
            q.limit(int(limit))
        return q.run(cls._conn)


class Site(BaseModel):
    __table__ = 'sites'

    @classmethod
    def get_by_name(cls, name):
        return get_one(cls.filter({'name': name}, limit=1))
