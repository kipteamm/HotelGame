from hotel.game.models import Player
from hotel.extensions import db, map_data

from flask_socketio import SocketIO, join_room

import random


def register_events(socketio: SocketIO):
    @socketio.on("join")
    def join(data: dict):
        player: Player | None = Player.query.get(data["session_token"])
        if not player:
            return
        
        join_room(player.game_id)
        socketio.emit("player_join", player.serialize(), to=player.game_id)
        return
    
    @socketio.on("roll_dice")
    def roll_dice(data: dict):
        player: Player | None = Player.query.filter_by(session_token=data["session_token"]).first()
        if not player:
            return

        socketio.emit("start_roll_dice", to=player.game_id)
        roll = random.randint(1, 6)

        moves = []
        for i in range(player.tile, player.tile + roll + 1):
            moves.append({"x": map_data.get_tile(i)["x"], "y": map_data.get_tile(i)["y"]})

        player.tile += roll
        player.pos_x = map_data.get_tile(player.tile)["x"]
        player.pos_y = map_data.get_tile(player.tile)["y"]
        db.session.commit()

        socketio.emit("stop_roll_dice", {"roll": roll, "player": player.serialize(), "tile": map_data.get_tile(player.tile), "moves": moves}, to=player.game_id)
        return
