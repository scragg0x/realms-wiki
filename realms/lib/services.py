import redis
from sqlalchemy import create_engine

# Default DB connection
from realms import config

db = create_engine(config.DB_URI, encoding='utf8', echo=True)

# Default Cache connection
cache = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT)