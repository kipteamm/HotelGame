const assets = {
    board: "/static/images/board.png",
    no_ambassador_lane: "/static/images/no_ambassador_lane.png",
    no_grandeur_avenue: "/static/images/no_grandeur_avenue.png",
    no_horizon_way: "/static/images/no_horizon_way.png",
    no_imperial_boulevard: "/static/images/no_imperial_boulevard.png",
};

document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("game");
    const ctx = canvas.getContext("2d");
    
    const images = {};
    const overlayImages = [
        "no_ambassador_lane", 
        // "no_grandeur_avenue", 
        // "no_horizon_way", 
        "no_imperial_boulevard"
    ];
    
    let scale = 0.5;
    let offsetX = 0, offsetY = 0;
    let startX, startY;
    let isDragging = false;

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        if (images.board) draw();
    }

    window.addEventListener("resize", resizeCanvas);
    resizeCanvas(); // Initialize on load

    // Load all assets (board + overlays)
    function loadAssets(callback) {
        let loaded = 0;
        const total = Object.keys(assets).length + overlayImages.length;

        // Load the main board
        images.board = new Image();
        images.board.onload = () => {
            loaded++;
            if (loaded === total) callback();
        };
        images.board.src = assets.board;

        // Load overlay images dynamically
        overlayImages.forEach(imageKey => {
            images[imageKey] = new Image();
            images[imageKey].onload = () => {
                loaded++;
                if (loaded === total) callback();
            };
            images[imageKey].src = assets[imageKey];
        });
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
        overlayImages.forEach(imageKey => {
            ctx.drawImage(images[imageKey], 0, 0, 2476, 2476); // Position at (0, 0) for simplicity, can be adjusted as needed
        });

        ctx.restore();
    }

    // Mouse events for panning
    canvas.addEventListener("mousedown", (e) => {
        isDragging = true;
        startX = e.clientX - offsetX;
        startY = e.clientY - offsetY;
    });

    canvas.addEventListener("mousemove", (e) => {
        if (isDragging) {
            offsetX = e.clientX - startX;
            offsetY = e.clientY - startY;
            draw();
        }
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

    loadAssets(draw);
});
