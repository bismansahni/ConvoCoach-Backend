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
    <title>Sign In to ConvoCoach</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            line-height: 1.5;
            min-height: 100vh;
            padding: 32px 16px;
        }}

        .container {{
            max-width: 672px;
            margin: 0 auto;
        }}

        .email-wrapper {{
            position: relative;
            background: linear-gradient(to bottom right, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.95));
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 16px;
            padding: 32px;
            overflow: hidden;
            box-shadow: 
                0 4px 6px -1px rgba(0, 0, 0, 0.1),
                0 2px 4px -1px rgba(0, 0, 0, 0.06),
                0 0 0 1px rgba(255, 255, 255, 0.1) inset;
        }}

        .glow {{
            position: absolute;
            top: 0;
            right: 0;
            bottom: 0;
            left: 0;
            background: radial-gradient(circle at 50% 0%, 
                rgba(29, 78, 216, 0.15),
                rgba(67, 56, 202, 0.1) 30%,
                transparent 70%) !important;
            opacity: 0.6;
            pointer-events: none;
        }}

        .logo-section {{
            text-align: center;
            margin-bottom: 32px;
        }}

        .logo-container {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}

        .logo {{
            width: 40px;
            height: 40px;
        }}

        .brand-name {{
            font-size: 30px;
            font-weight: 700;
            letter-spacing: -0.025em;
        }}

        .brand-name-dark {{
            color: #0f172a;
        }}

        .brand-name-gradient {{
            background: linear-gradient(135deg, #1d4ed8, #4338ca);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }}

        .content {{
            position: relative;
            z-index: 1;
            text-align: center;
        }}

        .title {{
            font-size: 20px;
            font-weight: 600;
            color: #0f172a;
            margin-bottom: 8px;
        }}

        .description {{
            color: #475569;
            margin-bottom: 24px;
        }}

        .button {{
            display: inline-block;
            background: linear-gradient(135deg, #1d4ed8, #4338ca);
            color: white !important;;
            text-decoration: none;
            padding: 12px 32px;
            border-radius: 12px;
            font-weight: 500;
            box-shadow: 0 10px 15px -3px rgba(29, 78, 216, 0.2);
            transition: all 0.3s ease;
        }}

        .button:hover {{
            background: linear-gradient(135deg, #1e40af, #3730a3);
            transform: translateY(-1px);
            box-shadow: 0 15px 20px -3px rgba(29, 78, 216, 0.3);
        }}

        .security-notice {{
            text-align: center;
            font-size: 14px;
            color: #64748b;
            margin-top: 32px;
        }}

        .security-notice p {{
            margin-bottom: 8px;
        }}

        .footer {{
            margin-top: 32px;
            padding-top: 24px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            font-size: 14px;
            color: #64748b;
        }}

        .footer p {{
            margin-bottom: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="email-wrapper">
            <div class="glow"></div>
            
            <!-- Logo Section -->
            <div class="logo-section">
                <div class="logo-container">
                    <svg class="logo" viewBox="0 0 706 646" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="logo-gradient" x1="30.62" y1="611.11" x2="422.65" y2="219.09" gradientUnits="userSpaceOnUse">
                                <stop offset="0" stop-color="#1d4ed8"/>
                                <stop offset=".98" stop-color="#4338ca"/>
                            </linearGradient>
                        </defs>
                        <circle fill="#4338ca" cx="513.87" cy="203.93" r="191.98"/>
                        <path fill="url(#logo-gradient)" d="M225.31,21.8c-26.01-27.64-69.94-29.41-97.14-2.94C59.35,85.86,0,208.75,0,306.01l3.2,227.67c0,55.23,34.26,112.24,114.14,112.24h343.69c39.35,0,71.25-31.9,71.25-71.25h0c0-35.78-26.59-65.87-62.05-70.63C215.38,469.81,174.18,223.88,235.88,101.88c13.39-26.48,9.91-58.31-10.42-79.92l-.15-.16Z"/>
                    </svg>
                    <h1 class="brand-name">
                        <span class="brand-name-dark">Convo</span>
                        <span class="brand-name-gradient">Coach</span>
                    </h1>
                </div>
            </div>

            <!-- Email Content -->
            <div class="content">
                <h2 class="title">Sign in to ConvoCoach</h2>
                <p class="description">Click the button below to securely sign in to your account.</p>

                <!-- Action Button -->
                <a href="{sign_in_link}" class="button">Sign in securely</a>

                <!-- Security Notice -->
                <div class="security-notice">
                    <p>This sign-in link will expire in 5 minutes.</p>
                    <p>If you didn't request this email, please ignore it.</p>
                </div>
            </div>

            <!-- Footer -->
            <div class="footer">
                <p>&copy; 2025 ConvoCoach. All rights reserved.</p>
                <p>This email was sent to {to_email}</p>
                <p> Do not reply to this email.</p>
            </div>
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