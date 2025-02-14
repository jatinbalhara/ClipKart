import os
import logging
import yt_dlp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define OAuth2 scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def authenticate_youtube():
    """ Authenticate user with OAuth2 and return a YouTube API client """
    creds = None

    # Check if token.json exists (stored credentials)
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no valid credentials exist, request login
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret_589693279046-5gku2vk45p61dok0c5b1b12jsvr5ktuj.apps.googleusercontent.com.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def get_uploaded_videos():
    """ Fetch the list of videos uploaded to your YouTube channel """
    try:
        youtube = authenticate_youtube()

        # Get the Uploads Playlist ID
        response = youtube.channels().list(part="contentDetails", mine=True).execute()
        uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        videos = []
        next_page_token = None

        while True:
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=next_page_token,
            )
            response = request.execute()

            if not response.get("items"):
                logging.error("No uploaded videos found.")
                break

            videos += response["items"]
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        # Extract video titles and IDs
        video_list = []
        for i, video in enumerate(videos, start=1):
            title = video["snippet"]["title"]
            video_id = video["snippet"]["resourceId"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_list.append((i, title, video_url))

        return video_list

    except HttpError as e:
        logging.error(f"YouTube API error: {e}")
        return None
    except Exception as e:
        logging.error(f"An error occurred while fetching the videos: {e}")
        return None

def download_video(youtube_url, output_path, filename):
    """ Download a YouTube video using yt-dlp """
    try:
        os.makedirs(output_path, exist_ok=True)

        ydl_opts = {
            'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'outtmpl': os.path.join(output_path, filename),
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        logging.info("Download completed!")

    except Exception as e:
        logging.error(f"An error occurred while downloading the video: {e}")

if __name__ == "__main__":
    # Fetch the list of uploaded videos
    videos = get_uploaded_videos()

    if videos:
        print("\n📌 Your Uploaded Videos:")
        for i, title, url in videos:
            print(f"{i}. {title} ({url})")

        # Let the user choose a video to download
        choice = input("\nEnter the number of the video you want to download (or 'exit' to quit): ")

        if choice.lower() != "exit" and choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(videos):
                selected_video = videos[choice - 1]
                print(f"\n📥 Downloading: {selected_video[1]}")
                output_path = "./downloads"
                filename = f"{selected_video[1].replace(' ', '_')}.mp4"

                # Download the selected video
                download_video(selected_video[2], output_path, filename)
            else:
                print("❌ Invalid choice. Exiting.")
        else:
            print("❌ Exiting without downloading.")
