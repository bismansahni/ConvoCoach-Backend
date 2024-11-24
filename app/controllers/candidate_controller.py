# import json
# import os
# from flask import request, jsonify

# def create_candidate_data():
#     try:
#         # Get the payload from the request
#         data = request.json
#         if not data:
#             return jsonify({"error": "No data provided"}), 400

#         # Define the file path for the JSON file
#         file_path = os.path.join(os.getcwd(), 'candidate-data.json')

#         # Save the data to a JSON file
#         with open(file_path, 'w') as json_file:
#             json.dump(data, json_file, indent=4)

#         return jsonify({"message": "Candidate data saved successfully!"}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500




import json
import os
from flask import request, jsonify
from google.cloud import firestore
from google.oauth2 import service_account


#TODO add interview status updates
def create_candidate_data():
    try:
        # Get the payload from the request
        data = request.json
        if not data or 'uid' not in data or 'interviewDocId' not in data:
            return jsonify({"error": "Missing required data (uid or interviewDocId)"}), 400

        # Extract UID and interview document ID from the payload
        uid = data['uid']
        interview_doc_id = data['interviewDocId']
        # print("UID:", uid)
        # print("Interview Doc ID:", interview_doc_id)

        # Initialize Firestore client using the service account key
        key_path = "service-key.json"  # Path to your service account key
        credentials = service_account.Credentials.from_service_account_file(key_path)
        db = firestore.Client(credentials=credentials)
        # print("Firestore client initialized!")

        # Fetch user document
        user_doc_ref = db.collection('users').document(uid)
        # print("User document reference:", user_doc_ref)
        user_doc = user_doc_ref.get()
        # print("User document fetched:", user_doc)

       
        
        # print("User document found!")

        user_data = user_doc.to_dict()
        candidate_name = user_data.get('name', 'Unknown')
        # print("Candidate Name:", candidate_name)
        current_role = user_data.get('currentRole', 'Unknown')
        # print("Current Role:", current_role)
        current_company = user_data.get('currentCompany', 'Unknown')
        # print("Current Company:", current_company)

        # Fetch interview details document
        interview_doc_ref = user_doc_ref.collection('interviewDetails').document(interview_doc_id)
        interview_doc = interview_doc_ref.get()

        # if not interview_doc.exists():
        #     return jsonify({"error": "Interview details not found"}), 404
        # print("here")

        interview_data = interview_doc.to_dict()

        # Combine the fetched data
        combined_data = {
            "candidateName": candidate_name,
            "currentRole": current_role,
            "currentCompany": current_company,
            "interviewDetails": interview_data,
            "uid": uid,
            "interviewDocId": interview_doc_id
        }

        print("Combined Data:", combined_data)

        # Define the file path for the JSON file
        file_path = os.path.join(os.getcwd(), 'candidate-data.json')

        # Save the data to a JSON file
        with open(file_path, 'w') as json_file:
            json.dump(combined_data, json_file, indent=4)

        return jsonify({"message": "Candidate data fetched and saved successfully!", "data": combined_data}), 200

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({"error": str(e), "details": error_details}), 500
