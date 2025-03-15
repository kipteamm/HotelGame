from hotel.utils.decorators import game_authorized
from hotel.game.models import Game, Player
from hotel.extensions import db, socketio

from flask import Blueprint, g


queue_blueprint = Blueprint("queue_api", __name__, url_prefix="/api/queue")


@queue_blueprint.delete("/leave")
@game_authorized
def leave_game():
    socketio.emit("player_leave", {"session_token": g.player.session_token}, to=g.player.game_id)

    if g.player.is_host:
        db.session.delete(Game.query.get(g.player.game_id))

    db.session.delete(g.player)
    db.session.commit()

    return {"success": True}, 204
