from email.mime.multipart import MIMEMultipart

from flask import request, jsonify
from firebase_admin import auth, firestore
from app.controllers.firebase_config import db

import firebase_admin
from firebase_admin import auth, credentials
import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, redirect, url_for




cred = credentials.Certificate("service-key.json")
print(cred)
# firebase_admin.initialize_app(cred)


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
            # "lastUpdated": datetime.now(timezone.utc)  # Correct usage
        }, merge=True)

        return jsonify({"message": "Feedback saved successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_sign_in_link_route():
    email_data = request.get_json()
    email = email_data.get('email')
    redirect_url = email_data.get('redirectUrl')
    print(email_data)
    print(email)
    print(redirect_url)# Frontend URL to redirect after clicking the link

    # Generate the sign-in link
    try:
        if not isinstance(redirect_url, str):
            raise ValueError("The redirect URL must be a string")
        action_code_settings = auth.ActionCodeSettings(
             url= redirect_url,
            handle_code_in_app = True,
    )
        print("we are here")
        # print(ActionCodeSettings)
        sign_in_link = auth.generate_sign_in_with_email_link(email,action_code_settings)
        print(sign_in_link)

        # Send the sign-in link via email using Gmail API
        return send_sign_in_link_email(email, sign_in_link)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400


SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_credentials():
    """Retrieve or refresh OAuth credentials."""
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds
#
# def send_sign_in_link_email(to_email, sign_in_link):
#     """Send sign-in link email using Gmail API."""
#     creds = get_credentials()
#     service = build('gmail', 'v1', credentials=creds)
#
#     html_content = f"""
#        <!DOCTYPE html>
#        <html lang="en">
#        <head>
#            <meta charset="UTF-8">
#            <meta name="viewport" content="width=device-width, initial-scale=1.0">
#            <title>Sign-In Link</title>
#            <style>
#                body {{
#                    font-family: Arial, sans-serif;
#                    background-color: #f7f7f7;
#                    color: #333;
#                    padding: 20px;
#                    margin: 0;
#                }}
#                .email-container {{
#                    width: 100%;
#                    max-width: 600px;
#                    margin: 0 auto;
#                    background-color: #ffffff;
#                    border-radius: 8px;
#                    padding: 20px;
#                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
#                }}
#                .email-header {{
#                    text-align: center;
#                    padding-bottom: 20px;
#                    border-bottom: 2px solid #f1f1f1;
#                }}
#                .email-header h1 {{
#                    color: #4CAF50;
#                    font-size: 24px;
#                }}
#                .email-body {{
#                    padding-top: 20px;
#                    text-align: center;
#                }}
#                .cta-button {{
#                    background-color: #4CAF50;
#                    color: white;
#                    padding: 14px 30px;
#                    text-decoration: none;
#                    font-size: 16px;
#                    border-radius: 5px;
#                    display: inline-block;
#                    margin-top: 20px;
#                }}
#                .email-footer {{
#                    text-align: center;
#                    padding-top: 30px;
#                    font-size: 12px;
#                    color: #999;
#                }}
#            </style>
#        </head>
#        <body>
#            <div class="email-container">
#                <div class="email-header">
#                    <h1>Convocoach: Sign In</h1>
#                </div>
#                <div class="email-body">
#                    <p>Hello,</p>
#                    <p>We received a request to sign in to your Convocoach account. To complete the sign-in process, please click the link below:</p>
#                    <a href="{sign_in_link}" class="cta-button">Sign In Now</a>
#                    <p>If you did not request this, please ignore this email.</p>
#                </div>
#                <div class="email-footer">
#                    <p>&copy; 2025 Convocoach. All rights reserved.</p>
#                </div>
#            </div>
#        </body>
#        </html>
#        """
#
#     # Create the sign-in link message
#     body = f"Click the link to sign in: {sign_in_link}"
#     message = MIMEText(body)
#     message['to'] = to_email
#     message['from'] = "Convocoach <noreply@convocoach.com>"
#     message['subject'] = "Sign-in Link"
#
#     # Encode the message to base64 and send
#     raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
#     message_body = {'raw': raw_message}
#
#     try:
#         # Send the email
#         service.users().messages().send(userId="me", body=message_body).execute()
#         return jsonify({"status": "success", "message": "Sign-in link sent successfully!"}), 200
#     except Exception as error:
#         return jsonify({"status": "error", "message": str(error)}), 500


def send_sign_in_link_email(to_email, sign_in_link):
    """Send sign-in link email using Gmail API."""
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    # Define the HTML content
    html_content = f"""
  <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sign-In Link</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f7f7f7;
                color: #333;
                padding: 20px;
                margin: 0;
            }}
            .email-container {{
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }}
            .email-header {{
                text-align: center;
                padding-bottom: 20px;
                border-bottom: 2px solid #f1f1f1;
            }}
            .email-header h1 {{
                color: #1d4ed8;
                font-size: 24px;
            }}
            .email-body {{
                padding-top: 20px;
                text-align: center;
            }}
            .cta-button {{
                background-color: #1d4ed8;
                color: white;
                padding: 14px 30px;
                text-decoration: none;
                font-size: 16px;
                border-radius: 5px;
                display: inline-block;
                margin-top: 20px;
            }}
            .email-footer {{
                text-align: center;
                padding-top: 30px;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>Convocoach: Sign In</h1>
            </div>
            <div class="email-body">
                <p>Hello,</p>
                <p>We received a request to sign in to your Convocoach account. To complete the sign-in process, please click the link below:</p>
                <a href="{sign_in_link}" class="cta-button">Sign In Now</a>
                <p>If you did not request this, please ignore this email.</p>
            </div>
            <div class="email-footer">
                <p>&copy; 2025 Convocoach. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Create a multipart message
    message = MIMEMultipart()
    message['to'] = to_email
    message['from'] = "Convocoach <noreply@convocoach.com>"
    message['subject'] = "Sign-in Link"

    # Attach the HTML content to the message
    msg = MIMEText(html_content, 'html')
    message.attach(msg)

    # Encode the message to base64
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw_message}

    try:
        # Send the email
        service.users().messages().send(userId="me", body=message_body).execute()
        return jsonify({"status": "success", "message": "Sign-in link sent successfully!"}), 200
    except Exception as error:
        return jsonify({"status": "error", "message": str(error)}), 500