from hotel.game.game_manager import Game
from hotel.utils.forms import validate_string
from hotel.auth.models import User    
from hotel.extensions import db

from flask_login import login_user, logout_user, current_user, AnonymousUserMixin
from flask import Blueprint, render_template, request, flash, redirect, make_response


auth_blueprint = Blueprint("auth", __name__, url_prefix="/")


@auth_blueprint.route("", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("auth/index.html")
        
    username, error = validate_string(request.form["username"], 1, 30, "username")
    if not username:
        flash(error, "error")
        return render_template("auth/index.html")
    
    game_id = request.form["game_id"]
    if not game_id:
        return redirect("/g?s=q")
    
    game = Game.query.get(game_id)
    if not game:
        flash("No game found with that ID", "error")
        return render_template("auth/index.html")

    return render_template("auth/index.html")


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    username, error = validate_string(request.form["username"], 1, 30, "username")
    if not username:
        flash(error, "error")
        return render_template("auth/register.html")
    
    password, error = validate_string(request.form["password"], 8, 255)
    if not password:
        flash(error, "error")
        return render_template("auth/register.html")

    user = User(password, username)

    db.session.add(user)
    db.session.commit()
        
    login_user(user)
    flash("Registration successful. Welcome!", "success")
    
    response = make_response(redirect(request.args.get("next", "/app/battles")))
    response.set_cookie("ut", user.set_token())
    return response


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    username = request.form.get("user")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()
    if not user:
        flash(f"Invalid username.", "error")
        return render_template("auth/login.html")
    
    if not user.check_password(password):
        flash(f"Invalid password.", "error")
        return render_template("auth/login.html")

    login_user(user)
    
    response = make_response(redirect(request.args.get("next", "/app/battles")))
    response.set_cookie("ut", user.set_token())
    return response


@auth_blueprint.get("/logout")
def logout():
    if isinstance(current_user, AnonymousUserMixin):
        return redirect("/auth/login")    
    
    logout_user()
    return redirect("/auth/login")
