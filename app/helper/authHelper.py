from flask import request, jsonify
from firebase_admin import auth

def apply_authentication(blueprint):
    """Attach Firebase authentication to any Flask blueprint."""
    @blueprint.before_request
    def verify_firebase_token():
        id_token = request.headers.get('Authorization')

        if not id_token:
            return jsonify({"error": "Missing Authorization Token"}), 401

        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(id_token)
            request.user_uid = decoded_token['uid']  # Attach user UID to request context
        except Exception as e:
            return jsonify({"error": "Invalid or expired token", "message": str(e)}), 401
