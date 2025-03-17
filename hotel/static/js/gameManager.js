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
    const _player = game.players.find(_player => _player.session_token === playerData.session_token);
    if (!_player) return;
    Object.assign(_player, playerData);

    if (playerData.session_token === player.session_token) {
        Object.assign(player, playerData);
    }

    let playerElm = document.getElementById(playerData.session_token);
    if (!playerElm) {
        playerElm = document.createElement("li");
        playerElm.id = playerData.session_token;
        document.getElementById("players").appendChild(playerElm);
    }

    playerElm.innerHTML = `${JSON.stringify(playerData)}`;
}

function awaitDice() {
    const playerAction = document.getElementById("dice-action");
    playerAction.classList.add("active");
    playerAction.innerHTML = `<h2>${player.colour === game.player? "You are": game.players.find(_player => _player.colour === game.player).username + " is"} rolling</h2><div class="dice" id="dice">6</div>`;
    
    if (player.colour !== game.player) return;
    playerAction.innerHTML += '<br><button onclick="rollDice()" id="roll-dice-btn">Roll dice</button>';
}

function rollDice() {
    if (player.colour !== game.player) return alert("Not your turn.");

    socket.emit("roll_dice", {"session_token": player.session_token});
}

let diceInterval;
let diceRolls = 0;
function startRollDice() {
    document.getElementById("roll-dice-btn")?.remove();
    const diceElement = document.getElementById("dice");
    diceRolls = 0;

    diceInterval = setInterval(() => {
        diceElement.innerText = Math.floor(Math.random() * 6) + 1;
        diceRolls++;
    }, 125);
}

async function stopRollDice(number, moves) {
    return new Promise(resolve => {
        const checkStop = async () => {
            if (diceRolls >= 8) {
                clearInterval(diceInterval);
                diceInterval = null;

                document.getElementById("dice").innerText = number;

                setTimeout(async () => {
                    document.getElementById("dice-action").classList.remove("active");
                    await movePlayer(moves);
                    resolve();
                }, 1500);
            } else {
                setTimeout(checkStop, 125);
            }
        };

        checkStop();
    });
}


function movePlayer(moves) {
    return new Promise(async (resolve) => {
        const player = game.players.find(_player => _player.colour === game.player);

        for (let i = 0; i < moves.length; i++) {
            const target = moves[i];

            await moveToPoint(player, target);
        }

        resolve();
    });
}

function moveToPoint(player, target) {
    return new Promise((resolve) => {
        const frames = 20;
        let frame = 0;

        const startX = player.pos_x;
        const startY = player.pos_y;
        const deltaX = (target.x - startX) / frames;
        const deltaY = (target.y - startY) / frames;

        function animate() {
            if (frame < frames) {
                player.pos_x += deltaX;
                player.pos_y += deltaY;
                draw();

                frame++;
                setTimeout(animate, 50);
            } else {
                player.pos_x = target.x;
                player.pos_y = target.y;
                draw();
                resolve();
            }
        }

        animate();
    });
}
