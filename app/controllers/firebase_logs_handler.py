

import logging
import sys
import os
from datetime import datetime

# Ensure 'logs' folder exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Create a new log file for each day
log_filename = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.txt")

# Configure logging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Create a console handler to also print logs in the terminal
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Get the root logger and add handlers
logger = logging.getLogger()
logger.addHandler(console_handler)

# Redirect stdout and stderr to log file and console
class LogCapture:
    """Captures all stdout and stderr logs and writes them to the log file"""

    def write(self, message):
        if message.strip():  # Avoid empty lines
            logger.info(message.strip())

    def flush(self):
        pass  # Required for sys.stdout redirection

sys.stdout = LogCapture()
sys.stderr = LogCapture()

print("✅ Logging setup complete! Logs will be saved in 'logs/' folder with a new file daily.")
