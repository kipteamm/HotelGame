from hotel.game.events import register_events
from hotel.game.views import game_blueprint
from hotel.auth.views import auth_blueprint

from .extensions import db, socketio, cache
from .secrets import SECRET_KEY
from .config import DEBUG

from flask_migrate import Migrate
from flask import Flask, request, redirect


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="/static")

    app.register_blueprint(game_blueprint)
    app.register_blueprint(auth_blueprint)

    register_events(socketio)

    app.config["DEBUG"] = DEBUG
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./db.sqlite3"

    migrate = Migrate()

    socketio.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    db.init_app(app)

    @socketio.on("disconnect")
    def handle_disconnect():
        print("disconnect")
        return

    return app