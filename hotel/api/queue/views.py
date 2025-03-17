from hotel.utils.decorators import game_authorized
from hotel.game.models import Game, Player
from hotel.extensions import db, socketio, map_data

from flask import Blueprint, g

import random


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


@queue_blueprint.patch("/start")
@game_authorized
def start_game():
    if not g.player.is_host:
        return {"error": "You are not hosting this game."}, 400
    
    colours = ["yellow", "red", "green", "blue"]
    players: list[Player] = Player.query.filter_by(game_id=g.player.game_id).all()
    random.shuffle(players)
    data = []

    for player in players:
        player.colour = colours.pop()
        player.money = 12000 if len(players) > 2 else 25000
        player.pos_x = map_data.starting_positions[player.colour]["x"]
        player.pos_y = map_data.starting_positions[player.colour]["y"]

        data.append(player.serialize())

    Game.query.filter_by(id=g.player.game_id).update({Game.stage: 1, Game.players: len(players)})
    db.session.commit()

    socketio.emit("start_game", data, to=g.player.game_id)
    return {"success": True}, 204
