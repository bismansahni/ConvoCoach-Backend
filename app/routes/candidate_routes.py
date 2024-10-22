from flask import Blueprint, request, jsonify
from app.controllers.candidate_controller import create_candidate_data

candidate_bp = Blueprint('candidate', __name__)

@candidate_bp.route('/create-candidate', methods=['POST'])
def start_interview():
    return create_candidate_data()
