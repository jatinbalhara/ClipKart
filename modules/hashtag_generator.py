import cv2
import librosa
import numpy as np
from collections import Counter
import os
import subprocess
import mediapipe as mp
import speech_recognition as sr
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string

# Ensure required NLTK resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose

# Step 1: Extract Key Frames from Video
def extract_key_frames(video_path, num_frames=5):
    video_capture = cv2.VideoCapture(video_path)
    frames = []
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    step = total_frames // num_frames

    for i in range(num_frames):
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, i * step)
        ret, frame = video_capture.read()
        if ret:
            frames.append(frame)

    video_capture.release()
    return frames

# Step 2: Extract Audio from Video
def extract_audio(video_path, output_audio_path):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at {video_path}")
    try:
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", output_audio_path, "-y"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to extract audio: {e}")

# Step 3: Detect Visual Content
def detect_visual_content(frames):
    mp_objectron = mp.solutions.objectron.Objectron(static_image_mode=True, model_name='Chair')
    visual_tags = set()

    for frame in frames:
        results = mp_objectron.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.detected_objects:
            for obj in results.detected_objects:
                visual_tags.add(obj.object_name)

    return list(visual_tags)

# Helper Function: Calculate Angle
def calculate_angle(point1, point2, point3):
    point1 = np.array([point1.x, point1.y])
    point2 = np.array([point2.x, point2.y])
    point3 = np.array([point3.x, point3.y])

    vector1 = point1 - point2
    vector2 = point3 - point2

    cosine_angle = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
    angle = np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))
    return angle

# Map Pose to Activity
def map_pose_to_activity(pose_landmarks):
    if not pose_landmarks:
        return None

    # Angle calculations for arms and legs
    left_arm_angle = calculate_angle(
        pose_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        pose_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
        pose_landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value],
    )
    right_arm_angle = calculate_angle(
        pose_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        pose_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
        pose_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value],
    )
    left_leg_angle = calculate_angle(
        pose_landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        pose_landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
        pose_landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value],
    )
    right_leg_angle = calculate_angle(
        pose_landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        pose_landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
        pose_landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value],
    )

    # Detecting poses
    if left_arm_angle < 30 and right_arm_angle < 30 and left_leg_angle > 150 and right_leg_angle > 150:
        return "YogaPose"  # Yoga pose with straightened legs and arms bent.
    elif left_arm_angle > 150 and right_arm_angle > 150 and left_leg_angle > 150 and right_leg_angle > 150:
        return "Stretching"  # Fully extended arms and legs.
    elif left_leg_angle < 90 and right_leg_angle < 90:
        return "Squatting"  # Squat position.
    elif left_arm_angle < 90 and right_arm_angle < 90 and left_leg_angle > 150 and right_leg_angle > 150:
        return "Push-up"  # Arms bent and body horizontal (push-up).
    elif left_leg_angle < 90 or right_leg_angle < 90:
        return "Lunge"  # Lunge pose.
    elif left_arm_angle > 160 and right_arm_angle > 160 and left_leg_angle > 150 and right_leg_angle > 150:
        return "PlankPose"  # Full plank position with straight arms and legs.
    elif left_leg_angle < 60 and right_leg_angle < 60:
        return "JumpingJack"  # Legs and arms spread out in a "V" shape.
    elif left_leg_angle > 150 and right_leg_angle > 150:
        return "HighKnees"  # One leg high up with other standing.
    elif left_leg_angle > 90 and right_leg_angle > 90:
        return "ChairPose"  # Sitting posture with bent knees.
    else:
        return "NULL"

# Step 4: Detect Actions (e.g., Poses)
def detect_actions(frames):
    with mp_pose.Pose(static_image_mode=True) as pose:
        activity_tags = set()

        for frame in frames:
            results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                activity = map_pose_to_activity(results.pose_landmarks.landmark)
                if activity:
                    activity_tags.add(activity)

    return list(activity_tags)

# Step 5: Analyze Audio for Tempo
def analyze_audio(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo

# Step 6: Map Tempo to Genre
def map_tempo_to_genre(tempo):
    if tempo < 60:
        return ["#Relaxing", "#ChillVibes"]
    elif 60 <= tempo < 90:
        return ["#Smooth", "#LoFiBeats"]
    elif 90 <= tempo < 120:
        return ["#PopMusic", "#FeelGood"]
    elif 120 <= tempo < 150:
        return ["#RockAndRoll", "#Dance"]
    else:  # 150+
        return ["#HighEnergy", "#EDM"]

# Step 7: Generate Hashtags from Keywords
def generate_hashtags_from_content(keywords, num_hashtags=10):
    word_freq = Counter(keywords)
    hashtags = [f"#{word.lower()}" for word, _ in word_freq.most_common(num_hashtags)]
    return hashtags

# Speech-to-Text Function
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as audio_file:
        audio = recognizer.record(audio_file)
    try:
        # Transcribe the audio to text using Google Speech Recognition
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Audio could not be understood"
    except sr.RequestError as e:
        return f"Error with speech recognition service: {e}"

# Function to clean and process the text for hashtags
def clean_and_process_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

def generate_hashtags_from_text(text, num_hashtags=10):
    tokens = clean_and_process_text(text)
    word_freq = Counter(tokens)
    hashtags = [f"#{word}" for word, _ in word_freq.most_common(num_hashtags)]
    return hashtags

# Main Hashtag Generator Pipeline
def hashtag_generator(video_path):
    frames = extract_key_frames(video_path)
    audio_output_path = "extracted_audio.wav"
    extract_audio(video_path, audio_output_path)

    # Step 1: Get Visual Content Tags
    visual_content_tags = detect_visual_content(frames)
    
    # Step 2: Get Action Tags (from Poses)
    actions = detect_actions(frames)
    
    # Step 3: Analyze Audio
    tempo = analyze_audio(audio_output_path)
    genre_tags = map_tempo_to_genre(tempo)

    # Step 4: Transcribe Audio to Text and Generate Text-Based Hashtags
    text = transcribe_audio(audio_output_path)
    text_hashtags = generate_hashtags_from_text(text)
    
    # Combine all keywords
    keywords = visual_content_tags + actions + genre_tags + text_hashtags
    hashtags = generate_hashtags_from_content(keywords)

    return hashtags

# Example Usage
if __name__ == "__main__":
    video_path = "S:/AOCQ7477.MOV"
    try:
        hashtags = hashtag_generator(video_path)
        print(f"Generated Hashtags for YouTube: {hashtags}")
    except Exception as e:
        print(f"Error: {e}")
