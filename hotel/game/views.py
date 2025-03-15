from hotel.game.models import Game, Player
from hotel.extensions import db

from flask_socketio import join_room
from flask import Blueprint, render_template, redirect, request


game_blueprint = Blueprint("game", __name__, url_prefix="/g")


@game_blueprint.get("")
def game():
    player: Player | None = Player.query.get(request.cookies.get("se_to"))
    if not player:
        return redirect("/")

    game: Game | None = Game.query.get(player.game_id)
    if not game:
        db.session.delete(player)
        db.session.commit()
        return redirect("/")

    return render_template("game/game.html", game=game.serialize(True), player=player.serialize())
