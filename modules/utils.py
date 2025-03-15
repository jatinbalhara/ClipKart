import json
import logging
import os

def setup_logging():
    # Create the logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(os.path.join(logs_dir, "project.log")), logging.StreamHandler()],
    )

def load_config(config_file):
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Config file '{config_file}' not found. Please create it and add your API key.")
        return {}
    except Exception as e:
        logging.error(f"Failed to load config file: {e}")
        return {}
    
download_progress_tracker = {}

def progress_hook(d, socketid, socketio):
    """ Callback function to emit progress updates via Socket.IO """
    global download_progress_tracker
    
    if d['status'] == 'downloading' and 'downloaded_bytes' in d and 'total_bytes' in d:
        downloaded = d["downloaded_bytes"]
        total = d["total_bytes"]

        if socketid not in download_progress_tracker:
            download_progress_tracker[socketid] = {"downloaded": 0, "total": total}

        # Update total progress
        download_progress_tracker[socketid]["downloaded"] = downloaded
        compiled_progress = (downloaded / total) * 100

        socketio.emit("download_progress", {"percent": round(compiled_progress, 2)}, to=socketid)
        logging.info(f"Download Progress (Compiled): {compiled_progress}%")
    if d["status"] == "finished":
        logging.info("Download completed!")
        socketio.emit("download_progress", {"percent": 100}, to=socketid)
        download_progress_tracker.pop(socketid, None)
        
def update_editing_progress(socketid, socketio, percent):
    if isinstance(percent, (int, float)):  # ✅ Ensure it's a number
        socketio.emit("editing_progress", {"percent": percent}, to=socketid)
    else:
        logging.error(f"Invalid progress value: {percent}")
