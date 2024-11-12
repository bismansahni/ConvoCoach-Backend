
import os
from flask import jsonify
import stripe




from flask import request, jsonify
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

def create_payment():
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    # Extract data from the request (assuming these fields are sent from the frontend)
    data = request.json
    name = data.get('name')
    address = data.get('address')
    billing_address = data.get('billing_address')
    coupon_code = data.get('coupon_code')

    try:
        # Optionally validate and process coupon code logic here
        # For example, if you manage coupons manually, adjust the `amount` based on the coupon

        # Create a PaymentIntent with additional customer details
        payment_intent = stripe.PaymentIntent.create(
            amount=1200,  # Adjust amount as needed based on coupon, if applicable
            currency='usd',
            automatic_payment_methods={'enabled': True},
            shipping={
                'name': name,
                'address': {
                    'line1': address.get('line1', ''),
                    'city': address.get('city', ''),
                    'state': address.get('state', ''),
                    'postal_code': address.get('postal_code', ''),
                    'country': address.get('country', ''),
                },
            },
            metadata={
                'billing_address_line1': billing_address.get('line1', ''),
                'billing_city': billing_address.get('city', ''),
                'billing_state': billing_address.get('state', ''),
                'billing_postal_code': billing_address.get('postal_code', ''),
                'billing_country': billing_address.get('country', ''),
                'coupon_code': coupon_code or ''
            }
        )
        print(f"Payment intent created: {payment_intent['id']}")
        return jsonify({
            'clientSecret': payment_intent['client_secret']
        })
    except Exception as e:
        print(f"Error creating PaymentIntent: {e}") 
        return jsonify(error=str(e)), 403
