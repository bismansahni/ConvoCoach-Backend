from flask import request, jsonify
from datetime import datetime

# Example: In-memory session tracking
sessions = {"active_calls": 0, "call_logs": []}


def call_status():
    try:
        data = request.json
        status = data.get("status")
        timestamp = data.get("timestamp", datetime.utcnow().isoformat())

        if status == "call_joined":
            sessions["active_calls"] += 1
            print(f"Call joined at {timestamp}. Active calls: {sessions['active_calls']}")
        elif status == "call_ended":
            sessions["active_calls"] = max(sessions["active_calls"] - 1, 0)
            print(f"Call ended at {timestamp}. Active calls: {sessions['active_calls']}")

        # Log the event
        sessions["call_logs"].append({"status": status, "timestamp": timestamp})

        return jsonify({"message": "Status recorded.", "sessions": sessions}), 200
    except Exception as e:
        print(f"Error handling call status: {str(e)}")
        return jsonify({"error": "Failed to record status.", "details": str(e)}), 500
