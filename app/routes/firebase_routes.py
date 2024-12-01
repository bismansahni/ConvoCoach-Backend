from flask import Blueprint, request, jsonify
from app.controllers.firebase_controller import login_user, register_user, verify_email

firebase_bp = Blueprint('firebase_controller', __name__)

@firebase_bp.route('/login', methods=['POST'])
def login_route():
    return login_user()




@firebase_bp.route('/signup', methods=['POST'])
def signup_route():
    return register_user()


@firebase_bp.route('/verify-email', methods=['POST'])
def email_verification():
    return verify_email()
