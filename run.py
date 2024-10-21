
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables from .env file
load_dotenv(find_dotenv(), override=True)

# Print environment variables for debugging
print("BASE_URL (before Flask):", os.getenv("BASE_URL"))
print("API_KEY (before Flask):", os.getenv("API_KEY"))

from app import create_app
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    print(f"Starting Flask server on port {port}")
    app.run(debug=False, port=port)
