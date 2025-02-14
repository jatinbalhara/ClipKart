from pytube import YouTube
import logging
import os
from moviepy.editor import VideoFileClip, AudioFileClip

def download_video(url, output_path, filename):
    try:
        # Apply the 403 fix
        yt = YouTube(url)
        yt.bypass_age_gate()  # Bypass age restriction if applicable

        # Try to get a combined stream with both video and audio
        stream = yt.streams.filter(progressive=True, file_extension="mp4", res="1080p").first()

        if stream:
            stream.download(output_path=output_path, filename=filename)
        else:
            logging.warning("1080p combined stream not available. Downloading video and audio separately.")
            video_stream = yt.streams.filter(adaptive=True, file_extension="mp4", only_video=True).order_by("resolution").desc().first()
            audio_stream = yt.streams.filter(adaptive=True, file_extension="mp4", only_audio=True).order_by("abr").desc().first()

            if not video_stream or not audio_stream:
                raise ValueError("No available video or audio streams found.")

            video_file = video_stream.download(output_path=output_path, filename="video_temp.mp4")
            audio_file = audio_stream.download(output_path=output_path, filename="audio_temp.mp4")

            video_clip = VideoFileClip(video_file)
            audio_clip = AudioFileClip(audio_file)
            final_clip = video_clip.set_audio(audio_clip)
            final_output_path = os.path.join(output_path, filename)
            final_clip.write_videofile(final_output_path, codec="libx264", audio_codec="aac")

            video_clip.close()
            audio_clip.close()
            os.remove(video_file)
            os.remove(audio_file)

        logging.info("Download completed!")
    except Exception as e:
        logging.error(f"An error occurred while downloading the video: {e}")