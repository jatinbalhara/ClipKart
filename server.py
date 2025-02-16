from flask import Flask, request, jsonify, render_template, Response
from modules.download_video import download_video
from modules.edit_video import crop_and_format_for_reel
from modules.hashtag_generator import hashtag_generator
from modules.upload_video import upload_video, get_authenticated_service
from modules.utils import setup_logging
import os
import logging
import uuid
from flask_cors import CORS
from asyncio import sleep
from flask_socketio import SocketIO
import time

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)
socketio = SocketIO(app)

FLASK_RUN_PORT = os.environ.get("FLASK_RUN_PORT", 5500)

setup_logging()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/process_video', methods=['POST'])
def process_video():
    """Handle video processing (download, edit, upload)."""
    try:
        if not request.form:
            return jsonify({"error": "Invalid request, expected form data"}), 400

        video_url = request.form.get("url")
        socketid = request.form.get("socketid")
        
        if not video_url:
            return jsonify({"error": "No YouTube URL provided"}), 400
        output_path = "downloads"
        os.makedirs(output_path, exist_ok=True)

        filename = f"{uuid.uuid4()}.mp4"
        input_path = os.path.join(output_path, filename)
        edited_file_path = os.path.join(output_path, f"{filename}_reel.mp4")

        socketio.emit("progress", {"progress": 20, "message": "Downloading video..."}, to=socketid)
        
        logging.info("Downloading the video...")
        
        downloaded_file = download_video(video_url, output_path, filename)
        time.sleep(2)
        if not downloaded_file:
            logging.error("Failed to download the video.")
            return jsonify({"error": "Failed to download the video"}), 500
        
        socketio.emit("progress", {"progress": 50, "message": "Editing video..."}, to=socketid)
        edited_file = crop_and_format_for_reel(downloaded_file, edited_file_path)
        time.sleep(2)
        
        if not edited_file:
            logging.error("Failed to edit the video.")
            return jsonify({"error": "Failed to edit the video"}), 500

        socketio.emit("progress", {"progress": 100, "message": "Processing complete!"}, to=socketid)
        
        return jsonify({
            "download_message": "Video downloaded successfully",
            "downloaded_file": downloaded_file,
            "edit_message": "Video edited successfully",
            "edited_file": edited_file
        })

    except Exception as e:
        logging.error(f"Error processing video: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join("downloads", file.filename)
    file.save(file_path)
    return jsonify({"message": "File uploaded successfully", "file": file_path})

if __name__ == "__main__":
    app.run(debug=True, port=FLASK_RUN_PORT)
    socketio.run(app, debug=True, port=FLASK_RUN_PORT)
