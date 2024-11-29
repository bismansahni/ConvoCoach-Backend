#
# import json
# import os
# import subprocess
# from threading import Thread
#
# import whisper
# import librosa
# import numpy as np
# from textblob import TextBlob
# from flask import request, jsonify
# from werkzeug.utils import secure_filename
# import firebase_admin
# from firebase_admin import credentials, firestore,storage
#
# from app.controllers.firebase_config import bucket
#
# # Load Whisper model
# model = whisper.load_model("base")
#
# # Define upload folder
# UPLOAD_FOLDER = "./recordings"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#
# if not firebase_admin._apps:
#     cred = credentials.Certificate("service-key.json")  # Path to your service account file
#     firebase_admin.initialize_app(cred, {
#         'storageBucket': 'ai-interviewer-9aeea.appspot.com'  # Your Firebase Storage bucket name
#     })
#
# # Initialize Firestore client
# db = firestore.client()
#
# # Initialize Firebase Storage bucket (this will be shared across your app)
# bucket = storage.bucket()  # This should now work because the bucket name is passed during initialization
#
#
#
# def upload_recording():
#     try:
#         if "file" not in request.files:
#             return jsonify({"error": "No file part in the request"}), 400
#
#         file = request.files["file"]
#         interview_id = request.form.get("interviewId")
#
#         if not interview_id:
#             return jsonify({"error": "Interview ID is required."}), 400
#
#         if file.filename == "":
#             return jsonify({"error": "No selected file."}), 400
#
#         # Save and convert file
#         filename = secure_filename(f"{interview_id}.webm")
#         file_path = os.path.join(UPLOAD_FOLDER, filename)
#         file.save(file_path)
#
#         converted_path = os.path.join(UPLOAD_FOLDER, f"{interview_id}.mp3")
#         subprocess.run(
#             ["ffmpeg", "-i", file_path, "-acodec", "libmp3lame", converted_path],
#             check=True
#         )
#         os.remove(file_path)
#
#         # Start transcription and analysis in a separate thread
#         thread = Thread(target=process_transcription, args=(interview_id,))
#         thread.start()
#
#         return jsonify({"message": "Recording uploaded and converted successfully.", "filePath": converted_path}), 200
#
#     except Exception as e:
#         return jsonify({"error": "Failed to upload or convert recording.", "details": str(e)}), 500
#
#
# def process_transcription(interview_id):
#     try:
#         audio_file_path = os.path.join(UPLOAD_FOLDER, f"{interview_id}.mp3")
#         if not os.path.exists(audio_file_path):
#             print(f"No recording found for Interview ID: {interview_id}")
#             return
#
#         # Transcription
#         result = model.transcribe(audio_file_path, language="en")
#         transcription = result["text"]
#
#         # Audio Analysis
#         y, sr = librosa.load(audio_file_path)
#         pitches, _ = librosa.piptrack(y=y, sr=sr)
#         avg_pitch = np.mean(pitches[pitches > 0]) if pitches.size > 0 else None
#         pitch_variability = np.std(pitches[pitches > 0]) if pitches.size > 0 else None
#
#         rms = librosa.feature.rms(y=y)
#         avg_loudness = np.mean(rms) if rms.size > 0 else None
#         loudness_variability = np.std(rms) if rms.size > 0 else None
#
#         pauses = librosa.effects.split(y, top_db=30)
#         num_pauses = len(pauses)
#         avg_pause_duration = np.mean([p[1] - p[0] for p in pauses]) / sr if len(pauses) > 0 else None
#
#         word_list = transcription.lower().split()
#         filler_count = sum(word_list.count(filler) for filler in ["um", "uh", "like", "you know", "I mean"])
#         total_words = len(word_list)
#
#         speaking_time = sum([seg["end"] - seg["start"] for seg in result.get("segments", [])]) / 60
#         words_per_minute = total_words / speaking_time if speaking_time else 0
#
#         sentiment = TextBlob(transcription).sentiment
#
#         confidence_score = max(0, min(1, (
#             (1 - min(pitch_variability, 500) / 500) +
#             (1 - filler_count / 10 if filler_count else 1) +
#             (avg_loudness * 100 if avg_loudness else 0.5) +
#             (1 - num_pauses / 10 if num_pauses else 1)
#         ) / 4))
#
#         # Save the analysis to Firestore
#         save_proper_analysis_to_database(interview_id, transcription, confidence_score, words_per_minute, filler_count,
#                                          avg_pitch, avg_loudness, sentiment)
#
#         # Clean up the file
#         os.remove(audio_file_path)
#
#     except Exception as e:
#         print(f"Failed to process transcription or analysis for Interview ID {interview_id}: {e}")
#
#
# def save_proper_analysis_to_database(interview_id, transcription, confidence_score, words_per_minute, filler_count,
#                                      avg_pitch, avg_loudness, sentiment):
#     try:
#
#         with open("candidate-data.json", "r") as file:
#             candidate_data = json.load(file)
#
#         uid = candidate_data["uid"]
#         interview_doc_id = candidate_data["interviewDocId"]
#         # Define the document reference in Firestore
#         interview_ref = db.collection("users").document(uid).collection("interviewDetails").document(interview_doc_id)
#
#         # Check if the interview document exists
#         interview_doc = interview_ref.get()
#         if not interview_doc.exists:
#             print(f"Interview document with ID {interview_id} does not exist.")
#             return
#
#         # Prepare analysis data
#         analysis_data = {
#             "transcription": transcription,
#             "confidence_score": round(float(confidence_score), 2),  # Convert to regular Python float
#             "words_per_minute": round(float(words_per_minute), 2),  # Convert to regular Python float
#             "filler_count": filler_count,
#             "avg_pitch": float(avg_pitch) if avg_pitch is not None else None,  # Convert to float if not None
#             "avg_loudness": float(avg_loudness) if avg_loudness is not None else None,  # Convert to float if not None
#             "sentiment": {
#                 "polarity": sentiment.polarity,
#                 "subjectivity": sentiment.subjectivity,
#             },
#             "timestamp": firestore.SERVER_TIMESTAMP,  # Add server-side timestamp
#         }
#
#         # Save the analysis data to Firestore under the interview's analysis subcollection
#         analysis_ref = interview_ref.collection("analysis").document("results")
#         analysis_ref.set(analysis_data)
#
#         print(f"Analysis data successfully saved for Interview ID: {interview_id}")
#     except Exception as e:
#         print(f"Failed to save analysis data for Interview ID {interview_id}: {e}")






import json
import os
import subprocess
from threading import Thread

import vosk
import librosa
import numpy as np
from textblob import TextBlob
from flask import request, jsonify
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Initialize Vosk model
vosk_model = vosk.Model("model/vosk-model-small-en-us-0.15")  # Path to your Vosk model directory

# Define upload folder
UPLOAD_FOLDER = "./recordings"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("service-key.json")  # Path to your service account file
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'ai-interviewer-9aeea.appspot.com'  # Your Firebase Storage bucket name
    })

# Initialize Firestore client
db = firestore.client()

# Initialize Firebase Storage bucket (this will be shared across your app)
bucket = storage.bucket()  # This should now work because the bucket name is passed during initialization


def upload_recording():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files["file"]
        interview_id = request.form.get("interviewId")

        if not interview_id:
            return jsonify({"error": "Interview ID is required."}), 400

        if file.filename == "":
            return jsonify({"error": "No selected file."}), 400

        # Save and convert file
        filename = secure_filename(f"{interview_id}.webm")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        converted_path = os.path.join(UPLOAD_FOLDER, f"{interview_id}.mp3")
        subprocess.run(
            ["ffmpeg", "-i", file_path, "-acodec", "libmp3lame", converted_path],
            check=True
        )
        os.remove(file_path)

        # Start transcription and analysis in a separate thread
        thread = Thread(target=process_transcription, args=(interview_id,))
        thread.start()

        return jsonify({"message": "Recording uploaded and converted successfully.", "filePath": converted_path}), 200

    except Exception as e:
        return jsonify({"error": "Failed to upload or convert recording.", "details": str(e)}), 500


# # Function to process transcription and perform audio analysis
# def process_transcription(interview_id):
#     try:
#         audio_file_path = os.path.join(UPLOAD_FOLDER, f"{interview_id}.mp3")
#         if not os.path.exists(audio_file_path):
#             print(f"No recording found for Interview ID: {interview_id}")
#             return
#
#         # Transcription using Vosk
#         transcription = transcribe_with_vosk(audio_file_path)
#
#         # Audio Analysis using librosa
#         y, sr = librosa.load(audio_file_path)
#         pitches, _ = librosa.piptrack(y=y, sr=sr)
#         avg_pitch = np.mean(pitches[pitches > 0]) if pitches.size > 0 else None
#         pitch_variability = np.std(pitches[pitches > 0]) if pitches.size > 0 else None
#
#         rms = librosa.feature.rms(y=y)
#         avg_loudness = np.mean(rms) if rms.size > 0 else None
#         loudness_variability = np.std(rms) if rms.size > 0 else None
#
#         pauses = librosa.effects.split(y, top_db=30)
#         num_pauses = len(pauses)
#         avg_pause_duration = np.mean([p[1] - p[0] for p in pauses]) / sr if len(pauses) > 0 else None
#
#         word_list = transcription.lower().split()
#         filler_count = sum(word_list.count(filler) for filler in ["um", "uh", "like", "you know", "I mean"])
#         total_words = len(word_list)
#
#         speaking_time = sum([seg["end"] - seg["start"] for seg in transcription.get("segments", [])]) / 60
#         words_per_minute = total_words / speaking_time if speaking_time else 0
#
#         sentiment = TextBlob(transcription).sentiment
#
#         confidence_score = max(0, min(1, (
#             (1 - min(pitch_variability, 500) / 500) +
#             (1 - filler_count / 10 if filler_count else 1) +
#             (avg_loudness * 100 if avg_loudness else 0.5) +
#             (1 - num_pauses / 10 if num_pauses else 1)
#         ) / 4))
#
#         # Save the analysis to Firestore
#         save_proper_analysis_to_database(interview_id, transcription, confidence_score, words_per_minute, filler_count,
#                                          avg_pitch, avg_loudness, sentiment)
#
#         # Clean up the file
#         os.remove(audio_file_path)
#
#     except Exception as e:
#         print(f"Failed to process transcription or analysis for Interview ID {interview_id}: {e}")
#
#
# # Function to transcribe audio using Vosk

def process_transcription(interview_id):
    try:
        audio_file_path = os.path.join(UPLOAD_FOLDER, f"{interview_id}.mp3")
        if not os.path.exists(audio_file_path):
            print(f"No recording found for Interview ID: {interview_id}")
            return

        # Transcription using Vosk
        rec = vosk.KaldiRecognizer(vosk_model, 16000)  # Set the sampling rate to 16000 (adjust if needed)
        transcription = ""

        # Read audio file and process with Vosk
        with open(audio_file_path, "rb") as audio_file:
            audio_data = audio_file.read()
            if rec.AcceptWaveform(audio_data):
                result = json.loads(rec.Result())  # Get transcription result
                transcription = result["text"]
            else:
                print(f"Failed to transcribe audio for Interview ID: {interview_id}")

        print(f"Transcription for {interview_id}: {transcription}")

        # Audio Analysis using librosa
        y, sr = librosa.load(audio_file_path)
        pitches, _ = librosa.piptrack(y=y, sr=sr)
        avg_pitch = np.mean(pitches[pitches > 0]) if pitches.size > 0 else None
        pitch_variability = np.std(pitches[pitches > 0]) if pitches.size > 0 else None

        rms = librosa.feature.rms(y=y)
        avg_loudness = np.mean(rms) if rms.size > 0 else None
        loudness_variability = np.std(rms) if rms.size > 0 else None

        pauses = librosa.effects.split(y, top_db=30)
        num_pauses = len(pauses)
        avg_pause_duration = np.mean([p[1] - p[0] for p in pauses]) / sr if len(pauses) > 0 else None

        word_list = transcription.lower().split()
        filler_count = sum(word_list.count(filler) for filler in ["um", "uh", "like", "you know", "I mean"])
        total_words = len(word_list)

        # Calculate speaking time and words per minute
        speaking_time = len(y) / sr / 60  # Assuming 1 second of audio corresponds to 1 word
        words_per_minute = total_words / speaking_time if speaking_time else 0

        sentiment = TextBlob(transcription).sentiment

        confidence_score = max(0, min(1, (
                (1 - min(pitch_variability, 500) / 500) +
                (1 - filler_count / 10 if filler_count else 1) +
                (avg_loudness * 100 if avg_loudness else 0.5) +
                (1 - num_pauses / 10 if num_pauses else 1)
        ) / 4))

        # Save the analysis to Firestore
        save_proper_analysis_to_database(interview_id, transcription, confidence_score, words_per_minute, filler_count,
                                         avg_pitch, avg_loudness, sentiment)

        # Clean up the file
        os.remove(audio_file_path)

    except Exception as e:
        print(f"Failed to process transcription or analysis for Interview ID {interview_id}: {e}")


def transcribe_with_vosk(audio_file_path):
    try:
        # Initialize the recognizer
        recognizer = vosk.KaldiRecognizer(vosk_model, 16000)
        with open(audio_file_path, "rb") as audio_file:
            # Read audio file in chunks
            while True:
                data = audio_file.read(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    pass

            # Get transcription result
            result = recognizer.Result()
            transcription = json.loads(result).get("text", "")
            return transcription

    except Exception as e:
        print(f"Error during transcription with Vosk: {e}")
        return ""


# Function to save analysis to Firestore
def save_proper_analysis_to_database(interview_id, transcription, confidence_score, words_per_minute, filler_count,
                                     avg_pitch, avg_loudness, sentiment):
    try:
        # Load candidate data from file
        with open("candidate-data.json", "r") as file:
            candidate_data = json.load(file)

        uid = candidate_data["uid"]
        interview_doc_id = candidate_data["interviewDocId"]

        # Define the document reference in Firestore
        interview_ref = db.collection("users").document(uid).collection("interviewDetails").document(interview_doc_id)

        # Check if the interview document exists
        interview_doc = interview_ref.get()
        if not interview_doc.exists:
            print(f"Interview document with ID {interview_id} does not exist.")
            return

        # Prepare analysis data to be saved
        analysis_data = {
            "transcription": transcription,
            "confidence_score": round(float(confidence_score), 2),  # Convert to regular Python float
            "words_per_minute": round(float(words_per_minute), 2),  # Convert to regular Python float
            "filler_count": filler_count,
            "avg_pitch": float(avg_pitch) if avg_pitch is not None else None,
            "avg_loudness": float(avg_loudness) if avg_loudness is not None else None,
            "sentiment": {
                "polarity": sentiment.polarity,
                "subjectivity": sentiment.subjectivity,
            },
            "timestamp": firestore.SERVER_TIMESTAMP,
        }

        # Save analysis data to Firestore
        interview_ref.collection("analysis").document(interview_id).set(analysis_data)
        print(f"Analysis for Interview ID {interview_id} saved to Firestore.")

    except Exception as e:
        print(f"Error saving analysis to Firestore: {e}")
