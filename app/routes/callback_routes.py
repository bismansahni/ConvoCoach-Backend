from flask import Blueprint,request, jsonify

from app.controllers.callback_controller import tavus_callback

callback_bp = Blueprint('callback', __name__)

@callback_bp.route('/callback', methods=[ 'POST'])
def callback():
    return tavus_callback(request)
