from hotel.utils.data import MapData

from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO 
from flask_caching import Cache


socketio = SocketIO(cors_allowed_origins="*")
map_data = MapData("hotel/static/data/mapData.json")
cache = Cache(config={"CACHE_TYPE" : "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300})
db = SQLAlchemy()
