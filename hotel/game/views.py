from flask import Blueprint, render_template, redirect


game_blueprint = Blueprint("game", __name__, url_prefix="/g")


@game_blueprint.get("/<string:id>")
def game():
    return render_template("game/live_game.html")
