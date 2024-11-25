from flask import Blueprint, request, jsonify
from app.controllers.payment_controller import create_payment, stripe_webhook  # Corrected import

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/create_payment', methods=['POST'])
def create_payment_route():
    return create_payment()  


@payment_bp.route('/stripe_webhook', methods=['POST'])
def stripe_webhook_route():
    return stripe_webhook()