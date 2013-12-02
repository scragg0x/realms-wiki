import redis
from realms import config
from sqlalchemy import create_engine

# Default DB connection
db = create_engine(config.DB_URI, encoding='utf8', echo=True)

# Default Cache connection
cache = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT)