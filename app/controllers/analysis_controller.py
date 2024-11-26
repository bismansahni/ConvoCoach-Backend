import firebase_admin
from firebase_admin import credentials, firestore
import traceback
import json

def start_analysis():
    try:
        # Load candidate data from JSON
        with open("candidate-data.json", "r") as file:
            candidate_data = json.load(file)

        uid = candidate_data["uid"]
        interview_doc_id = candidate_data["interviewDocId"]

        # Read the transcription from the file
        with open("output.json", "r") as file:
            transcription = file.read()

        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            cred = credentials.Certificate("service-key.json")
            firebase_admin.initialize_app(cred)

        db = firestore.client()

        # Define the document reference in Firestore
        analysis_ref = db.collection("users").document(uid).collection("interviewDetails").document(interview_doc_id).collection("analysis")

        # Add the transcription under an "analysis" field
        # analysis_doc = {
        #     "transcription": transcription
        #    # Optional timestamp field
        # }
        # analysis_collection_ref.add(analysis_doc)

        transcription_doc_ref = analysis_ref.document("transcription")
        transcription_doc_ref.set({"transcription": transcription})
        print("Transcription added to 'analysis' collection successfully!")

    except Exception as e:
        print(f"Error uploading transcription: {traceback.format_exc()}")
        return {"error": str(e)}, 500