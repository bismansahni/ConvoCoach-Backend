



from flask import Blueprint, request, jsonify
from app.controllers.persona_controller import create_persona

persona_bp = Blueprint('persona_bp', __name__)

# Route to handle persona creation request from client
@persona_bp.route('/create/persona', methods=['POST'])
def handle_create_persona():
    # Here, you can extract any data the client sends
    data = request.json
    client_code = data.get('code', None)  # Assuming client sends a "code"
    
    # Validate the code (in this case, ensure the code is 300)
    if client_code == 300:
        # If the code is valid, call the create_persona function
        print(f"Client code received and valid: {client_code}")
        
        result = create_persona()
        
        # Return the result of persona creation (either success or error)
        return result
    
    # If the code is not valid, return an error response
    return jsonify({"error": "Invalid code provided"}), 400
