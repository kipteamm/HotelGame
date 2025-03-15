from hotel.utils.snowflakes import SnowflakeGenerator 
from hotel.extensions import db

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

import secrets
import time


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    # Authentication
    id = db.Column(db.String(128), primary_key=True, default=SnowflakeGenerator.generate_id)
    password = db.Column(db.String(128), nullable=False)
    token = db.Column(db.String(128), nullable=True)
    battle_token = db.Column(db.String(128), nullable=True)
    
    moderator = db.Column(db.Boolean(), default=False)

    username = db.Column(db.String(30), nullable=False, unique=True)
    creation_timestamp = db.Column(db.Float(), nullable=False, unique=False)

    def __init__(self, password, username):
        self.set_password(password)
        self.username = username
        self.creation_timestamp = time.time()

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def set_battle_token(self) -> str:
        self.battle_token = secrets.token_urlsafe(64)
        db.session.commit()
        
        return self.battle_token
    
    def set_token(self) -> str:
        self.token = secrets.token_urlsafe(64)
        db.session.commit()

        return self.token

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
        }
