const socket = io();

socket.on("connect", function() {
    console.log("connect");
    socket.emit("join", {"token": getCookie("se_to")});
});

socket.on("player_join", function(data) {
    if (document.getElementById(data.session_token)) return;
    if (document.readyState !== 'loading') return addPlayer(data);
    document.addEventListener('DOMContentLoaded', function () {
        addPlayer(data);
    });
});