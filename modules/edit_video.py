from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
import logging
from modules.utils import update_editing_progress
from ffmpeg_progress_yield import FfmpegProgress
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import os
import threading
import time


def crop_and_format_for_reel(input_path, reel_output_path, socketid, socketio):
    def editing():
        try:
            video = VideoFileClip(input_path).subclip(0, 60)
            square_size = min(video.size)
            cropped_video = video.crop(width=square_size, height=square_size, x_center=video.w / 2, y_center=video.h / 2)
            resized_video = cropped_video.resize(width=1080)
            black_background = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=video.duration)
            final_video = CompositeVideoClip([black_background, resized_video.set_position("center")])
            
            temp_output_path = os.path.splitext(reel_output_path)[0] + "_temp.mp4"
            final_video.write_videofile(temp_output_path, codec="libx264", fps=final_video.fps)
        
        except Exception as e:
            logging.error(f"An error occurred while formatting the reel: {e}")
            socketio.emit("editing_progress", {"error": str(e)}, to=socketid)
            return None

    def fake_progress():
        total_duration = 20  # Total fake progress duration in seconds
        steps = 20  # Number of progress updates
        interval = total_duration / steps  # Time between updates
        progress = 0

        while progress < 100:
            progress += (100 / steps)
            socketio.emit("editing_progress", {"percent": progress}, to=socketid)
            time.sleep(interval)
        
    socketio.emit("editing_started", to=socketid)
    
    # Start fake progress in a separate thread
    fake_progress_thread = threading.Thread(target=fake_progress)
    fake_progress_thread.start()

    # Start actual editing in a separate thread
    editing_thread = threading.Thread(target=editing)
    editing_thread.start()

    return reel_output_path

    
