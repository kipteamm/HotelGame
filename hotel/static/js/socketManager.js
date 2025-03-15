const socket = io();

socket.on("connect", function() {
    console.log("connect");
    socket.emit("join", {"token": getCookie("se_to")});
});

socket.on("player_join", function(data) {
    if (document.getElementById(`queue-${data.session_token}`)) return;
    if (document.readyState !== 'loading') return addPlayer(data);
    document.addEventListener('DOMContentLoaded', function () {
        addPlayer(data);
    });
});

socket.on("player_leave", function(data) {
    game.players.splice(game.players.indexOf(game.players.find(player => player.session_token === data.session_token)), 1);
    document.getElementById(`queue-${data.session_token}`)?.remove();
});

socket.on("start_game", function(data) {
    data.forEach(player => updatePlayer(player))
    updateStage(1);
});

socket.on("update_players", (data) => data.forEach(player => updatePlayer(player)));