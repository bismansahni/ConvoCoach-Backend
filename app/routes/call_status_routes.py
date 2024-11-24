from flask import Blueprint
from app.controllers.call_status_controller import call_status

call_status_bp=Blueprint('call_status', __name__)

@call_status_bp.route('/call_status', methods=['POST'])
def handle_call_status():
    return call_status()