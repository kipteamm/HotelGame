const assets = {
    board: "/static/images/board.png",
    amb: "/static/images/no_ambassador_lane.png",
    gra: "/static/images/no_grandeur_avenue.png",
    hor: "/static/images/no_horizon_way.png",
    imp: "/static/images/no_imperial_boulevard.png",
    blue: "/static/images/blue.png",
    green: "/static/images/green.png",
    red: "/static/images/red.png",
    yellow: "/static/images/yellow.png",
};

let canvas;
let ctx;

document.addEventListener("DOMContentLoaded", () => {
    canvas = document.getElementById("game");
    ctx = canvas.getContext("2d");

    window.addEventListener("resize", resizeCanvas);
    // Mouse events for panning
    canvas.addEventListener("mousedown", (e) => {
        if (e.button === 2) return;
        isDragging = true;
        startX = e.clientX - offsetX;
        startY = e.clientY - offsetY;
    });

    canvas.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        offsetX = e.clientX - startX;
        offsetY = e.clientY - startY;
        draw();
    });

    canvas.addEventListener("mouseup", () => {
        isDragging = false;
    });

    // Mouse wheel event for zooming
    canvas.addEventListener("wheel", (e) => {
        e.preventDefault();
        const scaleFactor = 1.1;
        const mouseX = e.clientX - canvas.offsetLeft;
        const mouseY = e.clientY - canvas.offsetTop;
        const worldX = (mouseX - offsetX) / scale;
        const worldY = (mouseY - offsetY) / scale;

        if (e.deltaY < 0) {
            scale *= scaleFactor;
        } else {
            scale /= scaleFactor;
        }

        offsetX = mouseX - worldX * scale;
        offsetY = mouseY - worldY * scale;
        draw();
    });

    canvas.addEventListener("contextmenu", (e) => {
        e.preventDefault(); // Prevent default right-click menu

        const mouseX = e.clientX - canvas.offsetLeft;
        const mouseY = e.clientY - canvas.offsetTop;

        // Convert screen coordinates to image coordinates
        const imageX = (mouseX - offsetX) / scale;
        const imageY = (mouseY - offsetY) / scale;

        console.log(`Right-click at image coordinates: (${imageX.toFixed(2)}, ${imageY.toFixed(2)})`);

        game.players.find(_player => _player.colour === "blue").pos_x = imageX;
        game.players.find(_player => _player.colour === "blue").pos_y = imageY;
        draw(); // Redraw to update player position
    });
});

const images = {};
let roadConfiguration = new Set(game.road_configuration.split("_"));

let scale = 0.5;
let offsetX = 0, offsetY = 0;
let startX, startY;
let isDragging = false;

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    if (images.board) draw();
}

// Load all assets dynamically
function loadAssets() {
    let loaded = 0;

    Object.keys(assets).forEach(key => {
        images[key] = new Image();
        images[key].onload = () => {
            loaded++;
        };
        images[key].src = assets[key];
    });
}

// Setter & Getter for overlay images
function getRoadConfiguration() {
    return [...roadConfiguration];
}

function setRoadConfiguration(newImages) {
    roadConfiguration = new Set(newImages.split("_"));
    draw();
}

// Function to draw the board and overlay images
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(offsetX, offsetY);
    ctx.scale(scale, scale);

    // Draw the main board image
    ctx.drawImage(images.board, 0, 0, 2476, 2476);

    // Draw all overlay images
    roadConfiguration.forEach(imageKey => {
        if (images[imageKey]) {
            ctx.drawImage(images[imageKey], 0, 0, 2476, 2476);
        }
    });

    // Draw player icons (if applicable)
    game.players.forEach(player => {
        ctx.drawImage(images[player.colour], player.pos_x, player.pos_y, 100, 100);
    });

    ctx.restore();
}

loadAssets();

// Expose functions for external use
window.getRoadConfiguration = getRoadConfiguration;
window.setRoadConfiguration = setRoadConfiguration;
