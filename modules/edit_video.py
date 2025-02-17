from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
import logging
from modules.utils import update_editing_progress
from ffmpeg_progress_yield import FfmpegProgress
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import os
from tqdm import tqdm

def crop_and_format_for_reel(input_path, reel_output_path, socketid, socketio):
    try:
        video = VideoFileClip(input_path).subclip(0, 60)
        square_size = min(video.size)
        cropped_video = video.crop(width=square_size, height=square_size, x_center=video.w / 2, y_center=video.h / 2)
        resized_video = cropped_video.resize(width=1080)
        black_background = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=video.duration)
        final_video = CompositeVideoClip([black_background, resized_video.set_position("center")])
        
        temp_output_path = os.path.splitext(reel_output_path)[0] + "_temp.mp4"
        final_video.write_videofile(temp_output_path, codec="libx264", fps=final_video.fps)

        # Use FFmpeg to export the video with progress tracking
        ff = FfmpegProgress([
            "ffmpeg",
            "-i", temp_output_path,
            "-c:v", "libx264",
            "-preset", "fast",
            reel_output_path
        ])

        # Track progress and emit updates
        for progress in ff.run_command_with_progress():
            socketio.emit("editing_progress", {"percent": progress}, to=socketid)

        # Clean up temporary file
        os.remove(temp_output_path)

        # Ensure 100% completion
        socketio.emit("editing_progress", {"percent": 100}, to=socketid)
        logging.info("Editing completed successfully!")
        return reel_output_path

    except Exception as e:
        logging.error(f"An error occurred while formatting the reel: {e}")
        socketio.emit("editing_progress", {"error": str(e)}, to=socketid)
        return None
