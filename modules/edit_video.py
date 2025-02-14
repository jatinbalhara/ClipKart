from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
import logging

def crop_and_format_for_reel(input_path, reel_output_path):
    try:
        video = VideoFileClip(input_path).subclip(0, 60)
        square_size = min(video.size)
        cropped_video = video.crop(width=square_size, height=square_size, x_center=video.w / 2, y_center=video.h / 2)
        resized_video = cropped_video.resize(width=1080)
        black_background = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=video.duration)
        final_video = CompositeVideoClip([black_background, resized_video.set_position("center")])
        final_video.write_videofile(reel_output_path, codec="libx264")
        logging.info("Reel formatting completed!")
        return reel_output_path
    except Exception as e:
        logging.error(f"An error occurred while formatting the reel: {e}")