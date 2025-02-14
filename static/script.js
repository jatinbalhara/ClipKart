const API_BASE_URL = process.env.API_BASE_URL || "http://172.0.0.1:5500";

document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript Loaded!"); // Debugging
    const processVideoForm = document.getElementById("processVideoForm");

    if (!processVideoForm) {
        console.error("Process Video Form not found!");
        return;
    }

    processVideoForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevents redirection
        console.log("Form submission prevented!"); // Debugging

        const videoUrl = document.getElementById("videoUrlInput").value.trim();
        if (!videoUrl) {
            alert("Please enter a YouTube URL.");
            return;
        }

        let formData = new FormData();
        formData.append("url", videoUrl);

        try {
            let response = await fetch("${API_BASE_URL}/process_video", {
                headers: {
                    "Content-Type": "application/json"
                  },
                  body: JSON.stringify({ url: videoUrl })
            });


            if (!response.ok) throw new Error(data.error || "Unknown error");

            console.log("Downloaded file path:", data.file);
            alert(data.message);
            data = await response.json();

            alert(data.message);
            console.log("Downloaded file path:", data.file);

        } catch (error) {
            console.error("Error:", error);
            alert("Error downloading video: " + error.message);
        }
    });

    const uploadFileForm = document.getElementById("uploadFileForm");
    if (!uploadFileForm) {
        console.error("Upload File Form not found!");
        return;
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
});
