



import os
from flask import request, jsonify
import stripe
from dotenv import load_dotenv

load_dotenv()

def create_payment():
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
    amount = data.get('amount', '')  # Default to 0 if not provided
    print("Amount received hehe:", amount)

    # Convert amount to an integer to ensure correct data type for Stripe
    try:
        amount = int(amount)
    except ValueError:
        return jsonify({"error": "Invalid amount format. Amount must be a number."}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero."}), 400

    print("Amount received:", amount)

    try:
        discount_amount = 0
        if coupon_code:
            promotion_codes = stripe.PromotionCode.list(
                code=coupon_code,
                limit=1  # Assuming code uniqueness
            )
            if promotion_codes.data:
                promotion_code = promotion_codes.data[0]
                if promotion_code["coupon"]["amount_off"]:
                    discount_amount = promotion_code["coupon"]["amount_off"]
                elif promotion_code["coupon"]["percent_off"]:
                    discount_amount = amount * (promotion_code["coupon"]["percent_off"] / 100)
            else:
                return jsonify({"error": "Invalid coupon code"}), 400

        # Calculate the final amount after applying the discount
        final_amount = max(amount - discount_amount, 0)
        final_amount = int(final_amount)
        final_amount=final_amount*100  # Convert to integer for Stripe
        print("Final amount after discount:", final_amount)

        # Create a PaymentIntent with additional customer details
        payment_intent = stripe.PaymentIntent.create(
            amount=final_amount,  # Use the calculated final amount
            currency='usd',
            automatic_payment_methods={'enabled': True},
            shipping={
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
            'clientSecret': payment_intent['client_secret'],
            'discount_amount': discount_amount
        })
    except Exception as e:
        print(f"Error creating PaymentIntent: {e}")
        return jsonify(error=str(e)), 403
