from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO 
from flask_caching import Cache


socketio = SocketIO(cors_allowed_origins="*")
# cache = Cache(config={"CACHE_TYPE" : "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300})
cache = Cache(config={"CACHE_TYPE" : "RedisCache", "CACHE_REDIS_HOST": "localhost", "CACHE_REDIS_PORT": 6379, "CACHE_REDIS_DB": 0})
db = SQLAlchemy()