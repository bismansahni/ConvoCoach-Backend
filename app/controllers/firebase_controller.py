import os


from flask import request, jsonify
from firebase_admin import auth, firestore
from app.controllers.firebase_config import db




def login_user():
    try:
        # Parse JSON request to get the ID token
        data = request.get_json()
        id_token = data.get('idToken')
        # print(" we are here success!")

        # Validate the presence of the token
        if not id_token:
            return jsonify({"error": "ID token is required"}), 400

        # Verify the ID token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token.get('uid')

        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()

        # print(" we are here success!")

        if not user_doc.exists:
            return jsonify({"error": "User does not exist in Firestore"}), 404

        user_data = user_doc.to_dict()
        if not user_data.get('isEmailVerified', False):
            return jsonify({
                "error": "Email not verified",
                "message": "Please verify your email before logging in."
            }), 403


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
            'isEmailVerified': True,
            'credits': int(os.getenv("INITIAL_CREDITS")),
            'createdAt': firestore.SERVER_TIMESTAMP
        })

        return jsonify({"message": "User registered successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



def verify_email():
    try:
        # Parse the request body
        data = request.json
        uid = data.get('uid')  # User's UID

        if not uid:
            return jsonify({"error": "Missing uid"}), 400

        # Check if the user exists in Firestore
        user_ref = db.collection('users').document(uid)
        user = user_ref.get()

        if not user.exists:
            return jsonify({"error": "User not found"}), 404

        # Update the email verification flag
        user_ref.update({"isEmailVerified": True})

        return jsonify({"message": "Email verification successful"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500







def personal_feedback():
    try:
        # Parse the request JSON
        data = request.json
        print(data)
        uid = data.get('uid')
        interview_id = data.get('interviewId')

        # Validate the presence of required fields
        if not uid:
            return jsonify({"error": "Missing uid"}), 400
        if not interview_id:
            return jsonify({"error": "Missing interview_id"}), 400

        # Check if the user exists in Firestore
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()


        # Add personal feedback to Firestore
        feedback_ref = user_ref.collection('interviewDetails').document(interview_id).collection('analysis').document('personal_feedback')
        feedback_ref.set({
            **data,  # Save the data payload
              "timestamp": firestore.SERVER_TIMESTAMP  # Correct usage
        })

        # Update interview details to indicate feedback presence
        interview_ref = user_ref.collection('interviewDetails').document(interview_id)
        interview_ref.set({
            "hasFeedback": True,
            "lastUpdated": datetime.now(timezone.utc)  # Correct usage
        }, merge=True)

        return jsonify({"message": "Feedback saved successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500