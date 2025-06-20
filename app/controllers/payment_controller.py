


import os
from flask import request, jsonify
import stripe
from dotenv import load_dotenv
from firebase_admin import auth, initialize_app, firestore

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK
try:
    initialize_app()
except ValueError:
    pass  # Firebase already initialized

# Initialize Firestore
db = firestore.client()

def stripe_webhook():
    """
    Handle Stripe webhook events.
    """
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        # Verify the Stripe webhook
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

        event_type = event.get("type")
        print(f"Received webhook event: {event_type}")

        # Handle specific event types
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            firebase_uid = session["metadata"].get("firebaseUID")

            if not firebase_uid:
                print("Error: firebaseUID is missing in session metadata.")
                return jsonify({"error": "firebaseUID missing"}), 400

            checkout_session = stripe.checkout.Session.retrieve(
                session["id"],
                expand=["line_items"]
            )

            # Extract price_id from line_items
            line_items = checkout_session["line_items"]["data"]
            price_id = line_items[0]["price"]["id"]
            print(f"Price ID purchased received from webhook: {price_id}")
            # Log session and user data
            print(f"Payment completed for UID: {firebase_uid}")
            print("Session details:", session)

            # Save payment info to Firestore
            save_payment_to_db(firebase_uid, session,price_id)

        return jsonify({"status": "success"}), 200

    except stripe.error.SignatureVerificationError as e:
        print("Webhook signature verification failed:", e)
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        print("Webhook error:", e)
        return jsonify({"error": "Webhook error"}), 400

def create_payment():
    """
    Create a Stripe Checkout session for the user.
    """
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    FRONTEND_URL = os.getenv("FRONTEND_URL")

    try:
        # Retrieve and verify the Firebase ID token from the Authorization header
        id_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not id_token:
            return jsonify({"error": "Missing Firebase ID token"}), 401

        # Verify the Firebase token and extract user information
        decoded_token = auth.verify_id_token(id_token)
        firebase_uid = decoded_token.get("uid")
        if not firebase_uid:
            return jsonify({"error": "Invalid Firebase token"}), 401

        data = request.get_json()
        price_id = data.get("priceId")
        print("Price ID received:", price_id)
        if not price_id:
            return jsonify({"error": "Missing Price ID"}), 400

        # Create Stripe Checkout session with Firebase UID in metadata
        session = stripe.checkout.Session.create(
            line_items=[{"price":  price_id, "quantity": 1}],
            mode="payment",
            success_url=f"{FRONTEND_URL}/dashboard?success=true",
            cancel_url = f"{FRONTEND_URL}/dashboard/Payments",
            allow_promotion_codes=True,
            metadata={"firebaseUID": firebase_uid},  # Attach Firebase UID
        )

        #added promotion codes properly

        # Debugging log for the session
        print("Stripe Checkout session created:", session)

        # Return the Checkout session URL to the frontend
        return jsonify({"url": session.url})

    except stripe.error.StripeError as e:
        print("Stripe error:", e)
        return jsonify({"error": "Payment processing error"}), 500
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": str(e)}), 500



def increment_credit_counter(uid, price_id):
    """
    Increment user credits based on the purchased price_id.
    """
    try:
        # Fetch the user document
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            print(f"User document does not exist for UID: {uid}")
            return jsonify({"error": "User document not found"}), 404

        # Retrieve current credits
        current_credits = user_doc.to_dict()['credits']  # Guaranteed to exist



        if price_id == os.getenv("BASIC_PLAN"):
            print("Processing BASIC_PLAN credits")
            new_credits = current_credits + int(os.getenv("BASIC_PLAN_CREDITS"))
            print("new_credits", new_credits)
        elif price_id == os.getenv("PRO_PLAN"):
            print("Processing PRO_PLAN credits")
            new_credits = current_credits + int(os.getenv("PRO_PLAN_CREDITS"))
            print("new_credits", new_credits)
        else:
            print(f"Invalid price_id: {price_id}")
            return jsonify({"error": "Invalid price ID"}), 400

        # Update the user document with the new credits
        user_ref.update({'credits': new_credits})
        print(f"Credits updated. New credits: {new_credits}")

        return jsonify({"message": "Credits incremented successfully", "new_credits": new_credits}), 200
    except Exception as e:
        print(f"An error occurred while incrementing credits: {str(e)}")
        return jsonify({"error": str(e)}), 500



def save_payment_to_db(firebase_uid, session, price_id):
    """
    Save payment information to Firestore and increment user credits.
    """
    try:
        # Reference to user payments collection
        user_ref = db.collection("users").document(firebase_uid)
        payments_ref = user_ref.collection("payments")

        # Check for existing payment with the same Stripe session ID
        existing_payment = payments_ref.where("stripeSessionId", "==", session["id"]).get()
        if existing_payment and len(existing_payment) > 0:  # If payment already exists
            print(f"Payment already exists for session ID: {session['id']}")
            # Call increment_credit_counter anyway
            return increment_credit_counter(firebase_uid, price_id)

        # Prepare payment data
        payment_data = {
            "stripeSessionId": session["id"],
            "paymentIntentId": session.get("payment_intent"),
            "amount_total": session["amount_total"],
            "currency": session["currency"],
            "status": session["payment_status"],  # Status (e.g., "paid")
            "created": session["created"],  # Timestamp
        }

        # Add new payment data to Firestore
        payments_ref.add(payment_data)
        print(f"Payment data saved for user {firebase_uid}")

        # Increment user credits
        return increment_credit_counter(firebase_uid, price_id)

    except Exception as e:
        print("Error saving payment to database:", e)
        return jsonify({"error": "Database error"}), 500
