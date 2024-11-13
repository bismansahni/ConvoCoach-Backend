

import os
from flask import request, jsonify
import stripe
from dotenv import load_dotenv

load_dotenv()

def create_payment():
    # print("Creating payment intent")
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    print("Request Headers:", request.headers)
    print("Request Method:", request.method)
    print("Request Data:", request.json)

    # Extract data from the request with defaults
    data = request.json
    print("Data: ", data)
    name = data.get('name', '').strip() or 'Default Name'
    address = data.get('address', {}) or {}
    billing_address = data.get('billing_address', {}) or {}
    coupon_code = data.get('coupon_code', '')

    try:
        # Create a PaymentIntent with additional customer details
        payment_intent = stripe.PaymentIntent.create(
            amount=1200,  # Adjust amount as needed based on coupon, if applicable
            currency='usd',
            automatic_payment_methods={'enabled': True},
            shipping={
                # 'name': name,
                'address': {
                    'line1': address.get('line1', 'Unknown'),
                    'city': address.get('city', 'Unknown'),
                    'state': address.get('state', 'Unknown'),
                    'postal_code': address.get('postal_code', '00000'),
                    'country': address.get('country', 'US'),
                },
                  "name": name,
            },
          
            metadata={
                'billing_address_line1': billing_address.get('line1', ''),
                'billing_city': billing_address.get('city', ''),
                'billing_state': billing_address.get('state', ''),
                'billing_postal_code': billing_address.get('postal_code', ''),
                'billing_country': billing_address.get('country', ''),
                'coupon_code': coupon_code
            }
        )
        print(f"Payment intent created: {payment_intent['id']}")
        return jsonify({
            'clientSecret': payment_intent['client_secret']
        })
    except Exception as e:
        print(f"Error creating PaymentIntent: {e}")
        return jsonify(error=str(e)), 403
