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