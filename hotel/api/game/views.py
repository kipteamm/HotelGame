from hotel.utils.decorators import game_authorized
from hotel.game.models import Game, Player
from hotel.extensions import db, socketio, map_data

from flask import Blueprint, g


game_blueprint = Blueprint("game_api", __name__, url_prefix="/api/game")

COLOURS = ["blue", "green", "red", "yellow"]


@game_blueprint.patch("/end-turn")
@game_authorized
def end_turn():
    game: Game | None = Game.query.get(g.player.game_id)
    if not game:
        db.session.delete(g.player)
        db.session.commit()
        return {"error": "Game not found"}, 400
    
    player: Player = g.player
    if not player.colour == game.player:
        return {"error": "It's not your turn"}, 400
    
    next_player = COLOURS[(COLOURS.index(game.player) + 1) % game.players]
    print(next_player)

    game.player = next_player
    db.session.commit()

    socketio.emit("next_turn", {"player": next_player}, to=player.game_id)

    return {"success": True}, 204
