from hotel.game.models import Player

from flask_socketio import SocketIO, join_room


def register_events(socketio: SocketIO):
    @socketio.on("join")
    def join(data: dict):
        player: Player | None = Player.query.get(data["token"])
        if not player:
            return
        
        join_room(player.game_id)
        socketio.emit("player_join", player.serialize(), to=player.game_id)
        return
