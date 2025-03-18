from hotel.utils.decorators import game_authorized
from hotel.game.models import Game, Player
from hotel.extensions import db, socketio, map_data

from flask import Blueprint, g

import orjson


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
    game.player = next_player
    db.session.commit()

    socketio.emit("next_turn", {"next_player": next_player}, to=player.game_id)

    return {"success": True}, 204


@game_blueprint.patch("/buy/<string:hotel_name>")
@game_authorized
def buy_hotel(hotel_name: str):
    game: Game | None = Game.query.get(g.player.game_id)
    if not game:
        db.session.delete(g.player)
        db.session.commit()
        return {"error": "Game not found"}, 400
    
    player: Player = g.player
    if not player.colour == game.player:
        return {"error": "It's not your turn"}, 400
    
    hotel = map_data.get_hotel(hotel_name)
    if not hotel:
        return {"error": "Hotel not found"}, 400
    
    if not hotel_name in game.hotels:
        return {"error": "Someone already owns this hotel"}, 400
    
    if hotel["cost_of_land"] > player.money:
        return {"error": "You cannot afford to buy this hotel"}
    
    player_hotels: dict = orjson.loads(player.hotels)
    player_hotels[hotel_name] = {"buildings": 0, "stars": 0}

    player.hotels = orjson.dumps(player_hotels)
    player.money -= hotel["cost_of_land"]
    game.hotels = game.hotels.replace(hotel_name, "")

    next_player = COLOURS[(COLOURS.index(game.player) + 1) % game.players]
    game.player = next_player

    db.session.commit()
    socketio.emit("next_turn", {"next_player": next_player, "player": player.serialize(), "hotels": game.hotels}, to=player.game_id)

    return {"success": True}, 204
