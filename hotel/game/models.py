from hotel.extensions import db

import secrets
import orjson
import random
import string
import time


class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.String(128), primary_key=True)
    stage = db.Column(db.Integer(), default=0)

    player = db.Column(db.String(6), default="blue")
    players = db.Column(db.Integer(), default=1)

    road_configuration = db.Column(db.String(2), default="amb_imp")
    hotels = db.Column(db.String(86), default="boomerang,el_dorado,fujiyama,letoile,majestic,president,royal,safari,taj_mahal,waikiki")

    creation_timestamp = db.Column(db.Float(), nullable=False, unique=False)

    def __init__(self):
        while True:
            self.id = "".join(random.choices(string.digits, k=5))
            if not Game.query.get(self.id):
                break

        self.creation_timestamp = time.time()

    def serialize(self, players: bool=False) -> dict:
        data = {
            "id": self.id,
            "stage": self.stage,
            "player": self.player,
            "players": self.players,
            "road_configuration": self.road_configuration,
            "creation_timestamp": self.creation_timestamp,
            "hotels": self.hotels
        }

        if not players:
            return data
        
        data["players"] = [player.serialize() for player in Player.query.filter_by(game_id=self.id).all()]
        return data


class Player(db.Model):
    __tablename__ = 'players'
    
    session_token = db.Column(db.String(128), primary_key=True)
    game_id = db.Column(db.String(128), db.ForeignKey('games.id'), nullable=False)

    username = db.Column(db.String(128))
    is_host = db.Column(db.Boolean(), default=False)

    hotels = db.Column(db.String(500), default="{}")
    colour = db.Column(db.String(6), nullable=True)
    money = db.Column(db.Integer(), default=0)
    pos_x = db.Column(db.Integer(), default=0)
    pos_y = db.Column(db.Integer(), default=0)
    tile = db.Column(db.Integer(), default=0)
    action = db.Column(db.String(500), nullable=True, default=None)

    def __init__(self, game_id: str, username: str, is_host=False):
        self.session_token = secrets.token_urlsafe(64)
        self.game_id = game_id
        self.username = username
        self.is_host = is_host

    @classmethod
    def get_game(cls, session_token: str | None) -> tuple[bool, str]:
        if not session_token:
            return False, ""
        
        player: Player | None = cls.query.get(session_token)
        if not player:
            return False, ""
        
        game: tuple | None = Game.query.with_entities(Game.stage).filter_by(id=player.game_id).first()
        if not game:
            db.session.delete(player)
            db.session.commit()
            return False, ""
        
        return True, str(game[0])

    def serialize(self) -> dict:
        return {
            "session_token": self.session_token,
            "username": self.username,
            "is_host": self.is_host,
            "colour": self.colour,
            "money": self.money,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "tile": self.tile,
            "hotels": orjson.loads(self.hotels),
            "action": self.action
        }
