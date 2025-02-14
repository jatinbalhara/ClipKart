import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import yt_dlp  # Replacing youtube_dl with yt_dlp


def get_video_url(youtube_url):
    """ Open YouTube in a headless browser and extract the final video URL """
    logging.info("Opening YouTube in a headless browser...")

    # Set up headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome without a UI
    chrome_options.add_argument("--mute-audio")  # Mute the video playback
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--no-sandbox")  # Required for running as root in some environments

    # Use WebDriver Manager to get ChromeDriver automatically
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Open YouTube
        driver.get(youtube_url)
        time.sleep(5)  # Let the page load fully

        # Get the final video URL (YouTube may redirect)
        final_url = driver.current_url
        logging.info(f"Extracted video URL: {final_url}")

    finally:
        driver.quit()  # Close the browser

    return final_url

def download_video(youtube_url, output_path, filename):
    """ Download YouTube video using yt-dlp with headless browser """
    try:
        os.makedirs(output_path, exist_ok=True)

        # Use the extracted video URL from Selenium
        video_url = get_video_url(youtube_url)

        # Set up yt-dlp options
        ydl_opts = {
            'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'outtmpl': os.path.join(output_path, filename),
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        logging.info("Download completed!")
        # Return the path to the downloaded file
        
        file_path = os.path.join(output_path, filename)
        logging.info(f"Download completed! File saved at: {file_path}")
        return file_path

    except Exception as e:
        logging.error(f"An error occurred while downloading the video: {e}")
        return None