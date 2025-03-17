function getCookie(name) {
    const cookieString = document.cookie;
    const cookies = cookieString.split(';');

    for (const cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split('=');
        if (cookieName === name) {
            return cookieValue;
        }
    }

    return null;
}

if (document.readyState !== 'loading') {
    updateStage(game.stage);
} else {
    document.addEventListener('DOMContentLoaded', function () {
        updateStage(game.stage);
    });
}

function updateStage(stage) {
    document.querySelector(".stage.active")?.classList.remove("active");
    document.getElementById("stage-" + stage).classList.add("active");
}

function addPlayer(data) {
    game.players.push(data);
    document.getElementById("players-queue").innerHTML += `<li id="queue-${data.session_token}">${data.username}</li>`
}

async function leaveGame() {
    const response = await fetch("/api/queue/leave", {method: "DELETE", headers: {"Authorization": `Bearer ${getCookie("se_to")}`}});

    if (!response.ok) return processError(response);
    return window.location.href="";
}

async function startGame() {
    if (game.players.length < 2) return alert("You need to be with at least 2 players");
    const response = await fetch("/api/queue/start", {method: "PATCH", headers: {"Authorization": `Bearer ${getCookie("se_to")}`}});

    if (!response.ok) return processError(response);
    document.getElementById("stage-0").classList.remove("active");
    document.getElementById("stage-1").classList.add("active");
}

function updatePlayer(playerData) {
    const player = game.players.find(player => player.session_token === playerData.session_token);
    if (!player) return;
    Object.assign(player, playerData);

    let playerElm = document.getElementById(playerData.session_token);
    if (!playerElm) {
        playerElm = document.createElement("li");
        document.getElementById("players").appendChild(playerElm);
    }

    playerElm.innerHTML = `${JSON.stringify(playerData)}`;

}
