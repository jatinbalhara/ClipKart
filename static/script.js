console.log("JavaScript Loaded!");
const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:5500`;
const socket = io(API_BASE_URL);
let socketid = null;
let fakeEditingTimer = null;



const progressContainer = document.getElementById("progressContainer");
const progressBar = document.getElementById("progressBar");
const editingProgressBar = document.getElementById("editingProgressBar");
const style = document.querySelector('style');
style.textContent = '.progress.w-100.editing-progress { height: 5px !important; }';
const progressElement = document.querySelector('.progress.w-100');
(async () => {
    await setElementStyles(progressElement, { height: '20px' });
})();
const data = {
  progressBarClasses: progressElement.className,
  progressBarHeight: window.getComputedStyle(progressElement)['height'],
  progressContainerHeight: window.getComputedStyle(progressContainer)['height'],
}

if (progressContainer) {
    console.log("Hiding progress container");
    progressContainer.style.setProperty('display', 'none', 'important');
}else {
    console.error("Progress container not found!");
}

function simulateFakeEditingProgress(duration = 20000) {
    if (!editingProgressBar || !progressContainer) return;

    let progress = 0;
    const interval = 100; // Update every 100ms
    const increment = (interval / duration) * 100; // Calculate progress increment

    fakeEditingTimer = setInterval(() => {
        progress += increment;
        if (progress >= 100) {
            progress = 100; // Ensure it doesn't exceed 100%
            clearInterval(fakeEditingTimer);
            
            // Hide progress bar after 1 second
            setTimeout(() => {
                progressContainer.style.display = "none";
            }, 1000);
        }

        // Update the yellow progress bar
        editingProgressBar.style.width = `${progress}%`;
        editingProgressBar.innerText = `Editing: ${progress.toFixed(2)}%`;
    }, interval);
}

window.onload = function () {
    console.log("Attempting to connect to socket at:", API_BASE_URL);
    let lastDownloadProgress = 0;
    fakeEditingTimer = null;

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

    socket.on("download_progress", function (data) {
        if (!data || typeof data.percent === "undefined") return;  // Handle missing data
    
        let progress = data.percent;
    
        if (progress >= lastDownloadProgress) {
            console.log("Download Progress:", progress);
    
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
                progressBar.innerText = `Downloading: ${progress}%`;
                progressContainer.style.display = "flex";
            }
    
            lastDownloadProgress = progress;
        }
        if (progress >= 100) {
            simulateFakeEditingProgress(20000);
        }
    });

    socket.on("download_complete", function () {
        console.log("Download complete!");
        simulateFakeEditingProgress(20000); // 20 seconds
    });

    // socket.on("editing_progress", function (data) {
    //     if (!data || typeof data.percent === "undefined") return;

    //     let progress = data.percent;
    //     console.log("Editing Progress:", progress);

    //     if (fakeEditingTimer) {
    //         clearInterval(fakeEditingTimer); // Stop fake progress when real progress starts
    //         fakeEditingTimer = null;
    //     }

    //     if (progressBar) {
    //         progressBar.style.width = `${progress}%`;
    //         progressBar.innerText = `Editing: ${progress.toFixed(2)}%`;
    //     }

    //     if (progress >= 100) {
    //         setTimeout(() => {
    //             progressContainer.style.display = "none";
    //         }, 1000);
    //     }
    // });
};
    



// document.addEventListener("DOMContentLoaded", function () {
document.getElementById("processVideoForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const videoUrl = document.getElementById("videoUrlInput").value.trim();
    if (!videoUrl) {
        alert("Please enter a YouTube URL.");
    }
    const progressContainer = document.getElementById("progressContainer");
    if (progressContainer) {
        progressContainer.style.display = "flex";
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
else {
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
}

// });

