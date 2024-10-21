


from flask import Flask, request, Response, stream_with_context, url_for
from app.routes.persona_routes import persona_bp
from app.routes.conversation_routes import conversation_bp
import os
import time
import json
import traceback
from openai import OpenAI
from flask_cors import CORS
from dotenv import load_dotenv



load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("API_KEY")
print("Loaded API " +OPENAI_API_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Simple route for testing
    @app.route('/')
    def index():
        return 'Flask server is running!'

    # Route to handle chat completions
    @app.route("/chat/completions", methods=["POST"])
    def chat_completion():
        print("Chat completions route was triggered")
        try:
            full_url = request.host_url.rstrip('/') + url_for('chat_completion')
            print(f"Route URL: {full_url}")
            start_time = time.perf_counter()
            data = request.json
            messages = data.get("messages", [])
            print(messages)

            # Start the completion stream
            completion_stream = client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, stream=True
            )

            print(f"Time taken to start streaming: {time.perf_counter() - start_time}")

            # This function will stream the response chunk by chunk
            def generate():
                for chunk in completion_stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        print(f"Streaming chunk: {content}")

                        # Stream each chunk of response as it's received
                        yield f"data: {json.dumps({'choices': [{'delta': {'content': content}}]})}\n\n"

                # Mark the completion of the stream
                yield "data: [DONE]\n\n"

            # Return a streaming response to the client
            response = Response(stream_with_context(generate()), content_type="text/plain")
            return response

        except Exception as e:
            print(f"CHATBOT_STEP: {traceback.format_exc()}")
            return Response(str(e), content_type="text/plain", status=500)

    # Register the persona routes blueprint
    app.register_blueprint(persona_bp)

    # Register the conversation routes blueprint
    app.register_blueprint(conversation_bp)

    # Function to print all endpoints with base URL
    def print_routes(base_url):
        with app.test_request_context():
            for rule in app.url_map.iter_rules():
                methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
                endpoint_url = url_for(rule.endpoint, **{arg: f"<{arg}>" for arg in rule.arguments})
                print(f"{base_url}{endpoint_url} [{methods}]")

    # Get the base URL from environment variables, default to 'http://localhost:5000' if not set
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    print(f"Loaded BASE_URL: {base_url}")

    # Print all endpoints before returning the app
    print_routes(base_url)

    return app
