import json
import os
from flask import request, jsonify

def create_candidate_data():
    try:
        # Get the payload from the request
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Define the file path for the JSON file
        file_path = os.path.join(os.getcwd(), 'candidate-data.json')

        # Save the data to a JSON file
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        return jsonify({"message": "Candidate data saved successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
