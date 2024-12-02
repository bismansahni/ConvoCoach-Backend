from flask import request, jsonify

from app.controllers.firebase_config import db


def credit_decrement():
    try:
        data=request.get_json()
        uid = data.get('uid')
        if not uid:
            return jsonify({"error": "Missing uid"}), 400
        # Fetch the user document
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()

        # Get current credits and decrement
        current_credits = user_doc.to_dict()['credits']

        if current_credits > 0:
            new_credits = current_credits - 1
            user_ref.update({'credits': new_credits})
            print(f"Credits updated. New credits: {new_credits}")
            return jsonify({"message": "Credits decremented successfully", "new_credits": new_credits}), 200
        else:
            print("No credits available to deduct.")
            return "Error: No credits available to deduct."
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return f"Error: {str(e)}"





def check_credit():
    try:
        data=request.get_json()
        uid = data.get('uid')
        if not uid:
            return jsonify({"error": "Missing uid"}), 400
        # Fetch the user document
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()

        # Get current credits and decrement
        current_credits = user_doc.to_dict()['credits']  # Assume 'credits' key is always present

        if current_credits > 0:
            return jsonify({"message": "Credits available", "current_credits": current_credits}), 200
        else:
            print("No credits available to deduct.")
            return jsonify({"message": "No credits available", "current_credits": current_credits}), 403
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return f"Error: {str(e)}"
