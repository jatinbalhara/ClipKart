import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http

# Set your OAuth 2.0 client secrets file path
CLIENT_SECRETS_FILE = "S:\Documents\Project S\client_secret_589693279046-5gku2vk45p61dok0c5b1b12jsvr5ktuj.apps.googleusercontent.com.json"

# Define the API scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

def get_authenticated_service():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def upload_video(youtube, video_file, title, description, category_id, tags):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public"  # Change to "private" or "unlisted" if needed
        }
    }

    # Call the API's videos.insert method to create and upload the video
    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=googleapiclient.http.MediaFileUpload(video_file, chunksize=-1, resumable=True)
    )

    response = insert_request.execute()
    print(f"Upload successful! Video ID: {response['id']}")

def main():
    youtube = get_authenticated_service()
    video_file = "S:\Documents\Project S\Reel.mp4"
    title = "Haryanvi Bhajan"
    description = ""
    category_id = "10" 
    tags = ["haryanvi", "haryanvibhajan", "desi"]

    upload_video(youtube, video_file, title, description, category_id, tags)

if __name__ == "__main__":
    main()
