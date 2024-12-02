from flask import Blueprint, request, jsonify
from app.controllers.credit_controller import  credit_decrement

credit_bp = Blueprint('credit', __name__)

@credit_bp.route('/credit-decrement', methods=['POST'])
def credits():
    return credit_decrement()
