import psutil
from flask import Flask, request, Response, stream_with_context, url_for, jsonify

from app.controllers.firebase_logs_handler import *
from app.controllers.call_status_controller import call_status
from app.routes.additional_transcription_routes import additional_transcription_bp
from app.routes.call_status_routes import call_status_bp
from app.routes.callback_routes import callback_bp
from app.routes.credit_routes import credit_bp
from app.routes.firebase_routes import firebase_bp
from app.routes.persona_routes import persona_bp
from app.routes.conversation_routes import conversation_bp
from app.routes.candidate_routes import candidate_bp
from app.routes.payment_routes import payment_bp
import os
import time
import json
import traceback
from openai import OpenAI
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from flask_talisman import Talisman
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from app.controllers.firebase_config import db

load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("API_KEY")
print("Loaded API " + OPENAI_API_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

REQUEST_COUNT = Counter('flask_request_count', 'Total number of requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('flask_request_latency_seconds', 'Request latency', ['method', 'endpoint'])


def create_app():
    app = Flask(__name__)
    # CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, )
    # CORS(app, resources={r"/*": {"origins": "https://ai-interview-frontend-mu.vercel.app/"}}, supports_credentials=True, allow_headers=["Content-Type"], methods=["POST", "GET", "OPTIONS"])

    # CORS(app, supports_credentials=True)

    CORS(
        app,
        resources={r"/*": {"origins": "*"}},  # Allow all origins (*), restrict later if needed
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_response(jsonify({"message": "CORS preflight successful"}))  # Fix here
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response, 200  # Ensure it returns HTTP 200

    Talisman(app)

    # Simple route for testing
    @app.route('/')
    def index():
        return 'Flask server is running!'

    @app.route('/healthz', methods=['GET'])
    def healthz():
        """Health check endpoint."""
        try:
            # You can add additional health checks here if needed, e.g., database connectivity.
            return jsonify({"status": "healthy"}), 200
        except Exception as e:
            # In case of any failure, return an error response.
            return jsonify({"status": "unhealthy", "error": str(e)}), 500

    @app.before_request
    def start_timer():
        request.start_time = time.time()

    @app.after_request
    def record_metrics(response):
        # Add CORS headers to allow all origins
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Credentials"] = "true"  # Only if you need to support credentials

        # Record request metrics logic
        try:
            REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
            if hasattr(request, 'start_time'):
                latency = time.time() - request.start_time
                REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(latency)
        except Exception as e:
            # Logging or handling any error encountered during metrics recording
            print(f"Error in recording metrics: {e}")

        return response

    @app.route('/metrics')
    def metrics():
        return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)

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

    app.register_blueprint(payment_bp)
    # Register the persona routes blueprint
    app.register_blueprint(persona_bp)

    # Register the conversation routes blueprint
    app.register_blueprint(conversation_bp)
    app.register_blueprint(call_status_bp)
    app.register_blueprint(callback_bp)
    app.register_blueprint(firebase_bp)
    app.register_blueprint(additional_transcription_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(credit_bp)

    process = psutil.Process(os.getpid())
    cpu_now = psutil.cpu_percent(interval=0)
    mem_now = process.memory_info().rss / (1024 ** 2)

    print(f"CPU: {cpu_now}, Memory: {mem_now} MB")

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

    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

    # Print all endpoints before returning the app
    print_routes(base_url)

    process = psutil.Process(os.getpid())
    cpu_now_after = psutil.cpu_percent(interval=0)
    mem_now_after = process.memory_info().rss / (1024 ** 2)

    print(f"CPU during init function: {cpu_now_after}, Memory during init function: {mem_now_after} MB")

    return app
