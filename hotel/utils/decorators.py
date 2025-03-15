from hotel.game.models import Player

from functools import wraps
from flask import request, g


def game_authorized(f):
    @wraps(f)

    def _decorated_function(*args, **kwargs):
        authorization = request.authorization

        if not authorization:
            return {"error": "Authorization header not found."}, 401
        
        if not authorization.type == "bearer":
            return {"error": "Invalid authorization header, expected bearer."}, 401
        
        g.player = Player.query.filter_by(session_token=authorization.token).first()

        if not g.player:
            return {"error": "Invalid authorization header."}, 401

        return f(*args, **kwargs)
    return _decorated_function
