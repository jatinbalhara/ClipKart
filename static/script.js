// const API_BASE_URL = process.env.API_BASE_URL || "http://172.0.0.1:5500";
const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:5500`;

window.onload = function () {
    console.log("Attempting to connect to socket at:", API_BASE_URL);
    const socket = io(API_BASE_URL);
    let socketid = undefined;
    const progressBar = document.getElementById("progressBar");

    socket.on("connect", function () {
        console.log("Connected to socket!");
        socketid = socket.id;
        console.log("ID: " + socketid);
    });

    socket.on("connect_error", function (error) {
        console.error("Connection error:", error); // Log connection errors
    });

    socket.on("disconnect", function (reason) {
        console.warn("Disconnected from socket:", reason); // Log disconnection reasons
    });

    socket.on("progress", function (data) {
        console.log(`Progress: ${data.progress}% - ${data.message}`);
        progressBar.style.width = data.progress + "%";
        progressBar.innerText = data.progress + "%";
    });
};

console.log("JavaScript Loaded!");
document.getElementById("processVideoForm").addEventListener("submit", async function (event) {
    event.preventDefault();
    
    const videoUrl = document.getElementById("videoUrlInput").value.trim();
    if (!videoUrl) {
        alert("Please enter a YouTube URL.");
        return;
    }

    let formData = new FormData();
    formData.append("url", videoUrl);
    formData.append("socketid", socketid);

    try {
        let response = await fetch(`${API_BASE_URL}/process_video`, {
            method: "POST",
            body: formData
        })

        if (!response.ok) {
            let errorData = await response.json();
            throw new Error(errorData.error || "Unknown error");
        }

        let data = await response.json();
        console.log("Downloaded file path:", data.file);
        alert(data.message);

    } catch (error) {
        console.error("Error:", error);
        alert("Error downloading video: " + error.message);
    }
});


const uploadFileForm = document.getElementById("uploadFileForm");
if (!uploadFileForm) {
    console.error("Upload File Form not found!");
}

uploadFileForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    let formData = new FormData(event.target);

    try {
        let response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        let data;
        if (response.headers.get('content-type')?.includes('application/json')) {
            data = await response.json();
        } else {
            let dataText = await response.text();
            throw new Error(`Invalid JSON response: ${dataText}`);
        }

        if (!response.ok) {
            throw new Error(data.error || "Unknown error");
        }

        alert(data.message);
    } catch (error) {
        console.error('Error:', error);
        alert('There was an error processing your request: ' + error.message);
    }
});
