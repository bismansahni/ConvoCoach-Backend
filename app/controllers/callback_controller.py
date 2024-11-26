import traceback

from flask import jsonify

from app.controllers.analysis_controller import start_analysis
from app.controllers.format_controller import transcription_formatter


def tavus_callback(request):
    try:
        data = request.json
        # print(data)
        event_type = data.get("event_type")

        if event_type == "application.transcription_ready":
            conversation_id = data.get("conversation_id")
            transcript = data['properties'].get('transcript', [])
            print(f"Transcription for conversation {conversation_id}:")

            # Save transcription to "transcription.txt"
            with open("transcription.txt", "w") as file:
                for entry in transcript:
                    file.write(f"{entry['role']}: {entry['content']}\n")

            print("Transcription saved to transcription.txt")
            transcription_formatter()
            start_analysis()
            return jsonify({"status": "Transcription saved to transcription.txt"}), 200
        else:
            return jsonify({"status": f"Unhandled event: {event_type}"}), 200
    except Exception as e:
        print(f"Error processing callback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500