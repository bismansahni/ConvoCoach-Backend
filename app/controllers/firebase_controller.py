from flask import request, jsonify
from firebase_admin import auth, firestore
from app.controllers.firebase_config import db


def login_user():
    try:
        # Parse JSON request to get the ID token
        data = request.get_json()
        id_token = data.get('idToken')

        # Validate the presence of the token
        if not id_token:
            return jsonify({"error": "ID token is required"}), 400

        # Verify the ID token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token.get('uid')  # Get the user's unique ID

        # Optionally, fetch additional user details from Firebase
        user = auth.get_user(uid)

        # Construct the response with user details
        return jsonify({
            "message": "Login successful",
            "user": {
                "uid": user.uid,
                "email": user.email,
                "displayName": user.display_name
            }
        }), 200

    except auth.AuthError as e:
        # Handle token verification or other authentication errors
        return jsonify({"error": "Authentication failed", "details": str(e)}), 401
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


def register_user():
    try:
        data = request.json
        uid = data.get('uid')
        email = data.get('email')

        if not uid or not email:
            return jsonify({"error": "Missing uid or email"}), 400

        # Add user to Firestore
        db.collection('users').document(uid).set({
            'email': email,
            'isEmailVerified': False,
            'createdAt': firestore.SERVER_TIMESTAMP
        })

        return jsonify({"message": "User registered successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
