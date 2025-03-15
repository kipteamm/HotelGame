from hotel.game.models import Game, Player
from hotel.utils.forms import validate_string
from hotel.extensions import db

from flask import Blueprint, render_template, request, flash, redirect


auth_blueprint = Blueprint("auth", __name__, url_prefix="/")


@auth_blueprint.route("", methods=["GET", "POST"])
def index():
    exists, stage = Player.get_game(request.cookies.get("se_to"))
    if exists:
        return redirect("/g?s=" + stage)

    if request.method == "GET":
        return render_template("auth/index.html")
        
    username, error = validate_string(request.form["username"], 1, 30, "username")
    if not username:
        flash(error, "error")
        return render_template("auth/index.html")
        
    game_id = request.form["game_id"]
    if not game_id:
        game = Game()
        player = Player(game.id, username, True)

        db.session.add_all([game, player])
        db.session.commit()

        response = redirect("/g?s=0")
        response.set_cookie("se_to", player.session_token)

        return response
    
    game: Game | None = Game.query.get(game_id)
    if not game:
        flash("No game found with that ID", "error")
        return render_template("auth/index.html")
    
    if game.stage != 0:
        flash("This game has already started", "error")
        return render_template("auth/index.html")
    
    if Player.query.filter_by(game_id=game.id).count() == 4:
        flash("This game is full", "error")
        return render_template("auth/index.html")

    player = Player(game.id, username)
    db.session.add(player)
    db.session.commit()

    response = redirect("/g?s=0")
    response.set_cookie("se_to", player.session_token)

    return response


@auth_blueprint.get("/reset")
def reset():
    Game.query.delete()
    Player.query.delete()

    db.session.commit()
    return redirect("/")
