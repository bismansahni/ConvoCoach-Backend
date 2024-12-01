
from flask import Flask, request, Response, stream_with_context, url_for, jsonify

from app.controllers.call_status_controller import call_status
from app.routes.additional_transcription_routes import additional_transcription_bp
from app.routes.call_status_routes import call_status_bp
from app.routes.callback_routes import callback_bp
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
from flask_cors import CORS
from dotenv import load_dotenv
from flask_talisman import Talisman
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from app.controllers.firebase_config import db




load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("API_KEY")
print("Loaded API " +OPENAI_API_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

REQUEST_COUNT = Counter('flask_request_count', 'Total number of requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('flask_request_latency_seconds', 'Request latency', ['method', 'endpoint'])

def create_app():
    app = Flask(__name__)
    # CORS(app, resources={r"/*": {"origins": "*"}})
    # CORS(app, resources={r"/*": {"origins": "https://ai-interview-frontend-mu.vercel.app/"}}, supports_credentials=True, allow_headers=["Content-Type"], methods=["POST", "GET", "OPTIONS"])


    CORS(app, supports_credentials=True)
    Talisman(app)

    # Simple route for testing
    @app.route('/')
    def index():
        return 'Flask server is running!'

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

    # Route to handle Tavus callbacks
    # @app.route('/api/tavus-callback', methods=['POST'])
    # def tavus_callback():
    #     try:
    #         # Retrieve the callback data sent by Tavus
    #         data = request.json
    #         print(f"Received Tavus callback data: {data}")
    #
    #         # Add your processing logic here, e.g., logging or updating the database
    #         # Example: Process the event
    #         event_type = data.get("event_type")
    #         conversation_id = data.get("conversation_id")
    #         print(f"Event type: {event_type}, Conversation ID: {conversation_id}")
    #
    #         # Return a success response
    #         return jsonify({"status": "received"}), 200
    #     except Exception as e:
    #         print(f"Error processing Tavus callback: {traceback.format_exc()}")
    #         return jsonify({"error": str(e)}), 500

    # @app.route('/api/tavus-callback', methods=['POST'])
    # def tavus_callback():
    #     try:
    #         data = request.json
    #         event_type = data.get("event_type")
    #
    #         if event_type == "application.transcription_ready":
    #             conversation_id = data.get("conversation_id")
    #             transcript = data['properties'].get('transcript', [])
    #             print(f"Transcription for conversation {conversation_id}:")
    #             for entry in transcript:
    #                 print(f"{entry['role']}: {entry['content']}")
    #
    #             return jsonify({"status": "transcription logged"}), 200
    #         else:
    #             return jsonify({"status": f"Unhandled event: {event_type}"}), 200
    #     except Exception as e:
    #         print(f"Error processing callback: {traceback.format_exc()}")
    #         return jsonify({"error": str(e)}), 500

    # @app.route('/api/tavus-callback', methods=['POST'])

    # @app.route('/stripe_webhook', methods=['POST'])
    # def stripe_webhook():
    #     stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    #     payload = request.get_data(as_text=True)
    #     sig_header = request.headers.get("Stripe-Signature")
    #
    #     try:
    #         # Verify webhook signature
    #         event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    #
    #         # Handle the event
    #         if event['type'] == 'checkout.session.completed':
    #             session = event['data']['object']
    #             print("Payment completed session:", session)
    #             # Further processing
    #
    #         return jsonify({"status": "success"}), 200
    #
    #     except stripe.error.SignatureVerificationError as e:
    #         print("Webhook signature verification failed:", e)
    #         return jsonify({"error": "Invalid signature"}), 400
    #     except Exception as e:
    #         print("Webhook error:", e)
    #         return jsonify({"error": str(e)}), 400




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

    return app
