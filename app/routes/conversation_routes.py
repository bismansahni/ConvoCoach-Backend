from flask import Blueprint, request, jsonify
from app.controllers.conversation_controller import create_conversation

conversation_bp = Blueprint('conversation_bp', __name__)

# Route to handle conversation creation request from client
@conversation_bp.route('/create/conversation', methods=['POST'])
def handle_create_conversation():
    # Extract data from the client request
    data = request.json
    persona_id = data.get('persona_id', None)
    candidate_name = data.get('candidate_name', None)
    client_code = data.get('code', None)  # Assuming client sends a "code"

    # Validate the code (ensure it is 300, similar to persona creation)
    if client_code == 300:
        print(f"Client code received and valid: {client_code}")
        
        # Check if persona_id and candidate_name are provided
        if not persona_id or not candidate_name:
            return jsonify({"error": "persona_id and candidate_name are required"}), 400

        # Call the create_conversation function with persona_id and candidate_name
        conversation_id, error = create_conversation(persona_id, candidate_name)

        if error:
            # Return the error if conversation creation fails
            return jsonify({
                "message": "Failed to create conversation",
                "error": error
            }), 400

        # Return success response with conversation_id
        return jsonify({
            "message": "Conversation created successfully",
            "conversation_id": conversation_id
        }), 200

    # If the code is not valid, return an error response
    return jsonify({"error": "Invalid code provided"}), 400





# @conversation_bp.route('/chat/completions', methods=['POST'])
# def chat_completions():
#     return handle_chat_completions()


