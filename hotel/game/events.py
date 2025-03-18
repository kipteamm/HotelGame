from hotel.game.models import Player, Game
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

        road_configuration: tuple | None = Game.query.with_entities(Game.road_configuration).filter_by(id=player.game_id).first()
        if not road_configuration:
            return

        roll = random.randint(1, 6)
        original_roll = roll
        final_tile, final_tile_id = map_data.get_tile(road_configuration[0], player.tile, roll)

        while db.session.query(Player.session_token).filter_by(game_id=player.game_id, tile=final_tile_id).first(): # type: ignore
            roll += 1
            final_tile, final_tile_id = map_data.get_tile(road_configuration[0], player.tile, roll)

        moves = map_data.get_moves(road_configuration[0], player.tile, roll)

        if player.tile < 8 and player.tile + roll > 8:
            player.money += 2000

        player.tile = final_tile_id
        player.pos_x = final_tile["x"]
        player.pos_y = final_tile["y"]
        db.session.commit()

        socketio.emit("stop_roll_dice", {"roll": original_roll, "player": player.serialize(), "tile": map_data.get_tile_data(player.tile), "moves": moves}, to=player.game_id)
        return
