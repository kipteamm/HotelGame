from hotel.extensions import db

import random
import string
import time


class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.String(128), primary_key=True)
    creation_timestamp = db.Column(db.Float(), nullable=False, unique=False)

    def __init__(self):
        self.id = "".join(random.choices(string.digits, k=5))
        while Game.query.get(id):
            self.id = "".join(random.choices(string.digits, k=5))

        self.creation_timestamp = time.time()

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "creation_timestamp": self.creation_timestamp,
        }
