import redis
from flask.ext.sqlalchemy import SQLAlchemy
from realms import config

db = SQLAlchemy()

# Default Cache connection
cache = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT)