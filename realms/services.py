import rethinkdb as rdb
import redis

import config


# Default DB connection
db = rdb.connect(config.db['host'], config.db['port'], db=config.db['dbname'])

# Default Cache connection
cache = redis.StrictRedis(host=config.cache['host'], port=config.cache['port'])