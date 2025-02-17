from flask import Blueprint, request, jsonify
from app.controllers.candidate_controller import create_candidate_data
from firebase_admin import auth

from app.helper.authHelper import apply_authentication

candidate_bp = Blueprint('candidate', __name__)

apply_authentication(candidate_bp)

@candidate_bp.route('/create-candidate', methods=['POST'])
def start_interview():
    return create_candidate_data()
