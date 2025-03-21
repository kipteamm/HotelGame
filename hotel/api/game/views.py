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
    
    tile_data = map_data.get_tile_data(player.tile)
    if not tile_data["type"] == "buy":
        return {"error": "You are not on an action tile"}, 400
    
    if not hotel_name in tile_data["hotels"]:
        return {"error": "You are not on an action tile"}, 400
    
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
    socketio.emit("next_turn", {"next_player": next_player, "player": player.serialize(), "game": {"hotels": game.hotels}}, to=player.game_id)

    return {"success": True}, 204


@game_blueprint.get("/draw-card")
@game_authorized
def draw_card():
    game: Game | None = Game.query.get(g.player.game_id)
    if not game:
        db.session.delete(g.player)
        db.session.commit()
        return {"error": "Game not found"}, 400
    
    player: Player = g.player
    if not player.colour == game.player:
        return {"error": "It's not your turn"}, 400
    
    if not map_data.get_tile_data(player.tile)["type"] == "action":
        return {"error": "You are not on an action tile"}, 400

    action = map_data.get_random_action()
    player.action = action
    db.session.commit()

    socketio.emit("reveal_card", {"action": action}, to=player.game_id)

    return {"success": True}, 204


@game_blueprint.patch("/construct/<string:hotel_name>")
@game_authorized
def construct_hotel(hotel_name: str):
    game: Game | None = Game.query.get(g.player.game_id)
    if not game:
        db.session.delete(g.player)
        db.session.commit()
        return {"error": "Game not found"}, 400
    
    player: Player = g.player
    if not player.colour == game.player:
        return {"error": "It's not your turn"}, 400
    
    multiplier = 1
    if not map_data.get_tile_data(player.tile)["type"] == "construct":
        if not player.action == "One free construction phase." or not player.action == "Construction phase for half the prise.":
            return {"error": "You are not on an action tile"}, 400
        
        multiplier = 0 if player.action == "One free construction phase." else .5
        player.action = None
    
    hotels: dict = orjson.loads(player.hotels)
    hotel = hotels.get(hotel_name)
    if not hotel:
        return {"error": "You do not own this hotel."}, 400
    
    hotel_data = map_data.get_hotel(hotel_name)
    assert hotel_data is not None
    if hotel["buildings"] == hotel_data["buildings"]:
        return {"error": "This hotel is already max level"}, 400
    
    if (hotel_data[f"building_{hotel["buildings"]}"] * multiplier) > player.money:
        return {"error": "You cannot afford this upgrade"}, 400
    
    player.money -= (hotel_data[f"building_{hotel["buildings"]}"] * multiplier)
    hotel["stars"] = hotel_data["stars"][hotel["buildings"]]
    hotel["buildings"] += 1
    player.hotels = orjson.dumps(hotels)

    next_player = COLOURS[(COLOURS.index(game.player) + 1) % game.players]
    game.player = next_player

    db.session.commit()
    socketio.emit("next_turn", {"next_player": next_player, "player": player.serialize()}, to=player.game_id)

    return {"success": True}, 204


CONFIGURATIONS = ["amb_imp", "amb_hor", "gra_imp", "gra_hor"]


@game_blueprint.patch("/layout/<string:configuration>")
@game_authorized
def layout(configuration: str):
    game: Game | None = Game.query.get(g.player.game_id)
    if not game:
        db.session.delete(g.player)
        db.session.commit()
        return {"error": "Game not found"}, 400
    
    player: Player = g.player
    if not player.colour == game.player:
        return {"error": "It's not your turn"}, 400
    
    if not map_data.get_tile_data(player.tile)["type"] == "action":
        return {"error": "You are not on an action tile"}, 400
    
    if player.action != "Change the road layout.":
        return {"error": "You cannot perform this action"}, 400

    if configuration not in CONFIGURATIONS:
        return {"error": "Invalid configuration"}, 400
    
    current_configuration = map_data.get_road_tiles(game.road_configuration)
    new_configuration = map_data.get_road_tiles(configuration)
    invalid_tiles = [tile for tile in current_configuration if tile not in new_configuration]

    if db.session.query(Player.session_token).filter( # type: ignore
        Player.game_id==player.game_id,
        Player.tile.in_(invalid_tiles)
    ).first():
        return {"error": "Invalid configuration"}, 400

    next_player = COLOURS[(COLOURS.index(game.player) + 1) % game.players]
    game.player = next_player
    game.road_configuration = configuration
    player.action = None

    db.session.commit()
    socketio.emit("next_turn", {"next_player": next_player, "game": {"road_configuration": game.road_configuration}}, to=player.game_id)

    return {"success": True}, 204
