#
# DO NOT DELETE THE BELOW COMMENTED CODE, THIS IS THE PROPER CODE OF THE FILE WHICH FOR NOW WE HAVE EXCLUDED FROM THE PROJECT
#
# import json
# import os
# import subprocess
# from threading import Thread
# import shutil
#
# import openai
# from openai import OpenAI
#
#
# from flask import request, jsonify
# from werkzeug.utils import secure_filename
# import firebase_admin
# from firebase_admin import credentials, firestore, storage
# import textblob
# import numpy as np
# import librosa
# from textblob import TextBlob
#
#
#
# client=OpenAI(api_key=os.environ.get("API_KEY"), )
#
#
# # Define upload folder
# UPLOAD_FOLDER = "./recordings"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#
#
# if not firebase_admin._apps:
#     cred = credentials.Certificate("service-key.json")
#     firebase_admin.initialize_app(cred, {
#         'storageBucket': 'ai-interviewer-9aeea.appspot.com'
#     })
#
#
# db = firestore.client()
#
#
# bucket = storage.bucket()
#
#
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
#         # Save the file in its original format
#         filename = secure_filename(f"{interview_id}.webm")
#         file_path = os.path.join(UPLOAD_FOLDER, filename)
#         file.save(file_path)
#
#         # Start transcription and analysis in a separate thread
#         thread = Thread(target=process_transcription, args=(interview_id,))
#         thread.start()
#
#         return jsonify({"message": "Recording uploaded successfully.", "filePath": file_path}), 200
#
#     except Exception as e:
#         return jsonify({"error": "Failed to upload the recording.", "details": str(e)}), 500
#
#
#
#
#
#
#
#
#
#
# def process_transcription(interview_id):
#     try:
#         with open(f"recordings/{interview_id}.webm", "rb") as audio_file:
#             transcription = client.audio.transcriptions.create(
#                 model="whisper-1",
#                 language="en",
#                 file=audio_file,
#                 response_format="verbose_json",
#                 timestamp_granularities=["word"]
#             )
#             print("the statement is received from openai:")
#             print(transcription.words)
#             analyze_audio_and_transcription(interview_id, transcription.words)
#
#     except Exception as e:
#         print(f"An error occurred: {e}")
#
#
#
# def analyze_audio_and_transcription(interview_id, transcription_words):
#     try:
#         # Load the audio file for analysis
#         audio_file_path = f"recordings/{interview_id}.webm"
#         y, sr = librosa.load(audio_file_path)
#
#         # Pitch and loudness analysis
#         pitches, _ = librosa.piptrack(y=y, sr=sr)
#         avg_pitch = np.mean(pitches[pitches > 0]) if pitches.size > 0 else 0
#         pitch_variability = np.std(pitches[pitches > 0]) if pitches.size > 0 else 0
#
#         rms = librosa.feature.rms(y=y)
#         avg_loudness = np.mean(rms) if rms.size > 0 else 0
#         loudness_variability = np.std(rms) if rms.size > 0 else 0
#
#         # Pause detection
#         pauses = []
#         last_end = 0
#         speaking_time = 0
#         filler_count = 0
#         filler_words = ["um", "uh", "like", "you know", "I mean"]
#
#         for word in transcription_words:
#             gap = word.start - last_end
#             if gap > 0 and gap < 1.5:  # Natural pause threshold
#                 pauses.append(gap)
#             speaking_time += word.end - word.start
#             filler_count += 1 if word.word.lower() in filler_words else 0
#             last_end = word.end
#
#         num_pauses = len(pauses)
#         avg_pause_duration = np.mean(pauses) if pauses else 0
#
#         # Words per minute
#         speaking_time_minutes = speaking_time / 60
#         word_count = len(transcription_words)
#         words_per_minute = word_count / speaking_time_minutes if speaking_time_minutes > 0 else 0
#
#         # Sentiment analysis
#         transcription_text = " ".join([word.word for word in transcription_words])
#         sentiment = TextBlob(transcription_text).sentiment
#
#         # Confidence score calculation
#         confidence_score = max(0, min(1, (
#             (1 - min(pitch_variability, 500) / 500) +
#             (1 - filler_count / max(1, word_count)) +
#             (avg_loudness * 10 if avg_loudness else 0.5) +
#             (1 - num_pauses / 10 if num_pauses else 1)
#         ) / 4))
#
#
#
#         save_proper_analysis_to_database(
#             interview_id,
#             transcription_text,
#             confidence_score,
#             words_per_minute,
#             filler_count,
#             avg_pitch,
#             avg_loudness,
#             sentiment
#         )
#
#
#
#
#
#
#     except Exception as e:
#         print(f"An error occurred during analysis: {e}")
#         return None
#
#
# def delete_specific_recording(interview_id):
#     try:
#         # Construct the file path for the specific recording
#         file_path = os.path.join(UPLOAD_FOLDER, f"{interview_id}.webm")
#
#         # Check if the file exists before attempting to delete
#         if os.path.exists(file_path):
#             os.remove(file_path)
#             print(f"Recording {file_path} deleted successfully.")
#         else:
#             print(f"File {file_path} not found, nothing to delete.")
#
#     except Exception as e:
#         print(f"Error deleting recording for Interview ID {interview_id}: {e}")
#
# def save_proper_analysis_to_database(interview_id, transcription, confidence_score, words_per_minute, filler_count,
#                                      avg_pitch, avg_loudness, sentiment):
#     try:
#         # Load candidate data from file
#         with open("candidate-data.json", "r") as file:
#             candidate_data = json.load(file)
#
#         uid = candidate_data["uid"]
#         interview_doc_id = candidate_data["interviewDocId"]
#
#         # Define the document reference in Firestore
#         interview_ref = db.collection("users").document(uid).collection("interviewDetails").document(interview_doc_id)
#
#         # Check if the interview document exists
#         interview_doc = interview_ref.get()
#         if not interview_doc.exists:
#             print(f"Interview document with ID {interview_id} does not exist.")
#             return
#
#         # Prepare analysis data to be saved
#         analysis_data = {
#             "transcription": transcription,
#             "confidence_score": round(float(confidence_score), 2),  # Convert to regular Python float
#             "words_per_minute": round(float(words_per_minute), 2),  # Convert to regular Python float
#             "filler_count": filler_count,
#             "avg_pitch": float(avg_pitch) if avg_pitch is not None else None,
#             "avg_loudness": float(avg_loudness) if avg_loudness is not None else None,
#             "sentiment": {
#                 "polarity": sentiment.polarity,
#                 "subjectivity": sentiment.subjectivity,
#             },
#             "timestamp": firestore.SERVER_TIMESTAMP,
#         }
#
#         # Save analysis data to Firestore
#         interview_ref.collection("analysis").document("voice_details").set(analysis_data)
#         print(f"Analysis which is the new one for Interview ID {interview_id} saved to Firestore.")
#
#         delete_specific_recording(interview_id)
#
#     except Exception as e:
#         print(f"Error saving analysis to Firestore: {e}")
#
#
## DO NOT DELETE THE ABOVE COMMENTED CODE, THIS IS THE PROPER CODE OF THE FILE WHICH FOR NOW WE HAVE EXCLUDED FROM THE PROJECT
#
#
#





import os
from flask import request, jsonify

# Dummy Client
client = None

# Define upload folder
UPLOAD_FOLDER = "./recordings"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# db = firestore.client()
#
#
#  bucket = storage.bucket()
#

def upload_recording():
    print("Hi from upload_recording")
    # return jsonify({"message": "Dummy response"}), 200
    return jsonify({"message": "Recording uploaded successfully.", "filePath": "file_path"}), 200


def process_transcription():
    print("Hi from process_transcription")


def analyze_audio_and_transcription():
    print("Hi from analyze_audio_and_transcription")


def delete_specific_recording():
    print("Hi from delete_specific_recording")


def save_proper_analysis_to_database():
    print("Hi from save_proper_analysis_to_database")







