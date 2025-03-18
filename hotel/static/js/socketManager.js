const socket = io();

socket.on("connect", function() {
    console.log("connect");
    socket.emit("join", {"session_token": getCookie("se_to")});
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
    resizeCanvas();
    draw();
    awaitDice();
});

socket.on("next_turn", function(data) {
    game.player = data.next_player;
    awaitDice();

    updatePlayer(data.player);
    if (!data.hotels) return;
    game.hotels = data.hotels;
});

socket.on("update_players", (data) => data.forEach(player => updatePlayer(player)));

socket.on("start_roll_dice", (_) => startRollDice());

socket.on("stop_roll_dice", async function(data) {
    console.log(data);
    await stopRollDice(data.roll, data.moves);
    updatePlayer(data.player);

    if (data.tile.type !== "action") return playerActions(data.tile);
    awaitAction();
});

socket.on("reveal_card", (data) => revealCard(data));
