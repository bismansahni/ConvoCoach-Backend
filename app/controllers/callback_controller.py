


import traceback
import json
from flask import jsonify

from app.controllers.analysis_controller import save_transcription_to_database


def tavus_callback(request):
    """
    Callback function to process transcription and convert it into the required JSON format.
    """
    try:
        data = request.json
        event_type = data.get("event_type")

        if event_type == "application.transcription_ready":
            conversation_id = data.get("conversation_id")
            transcript = data['properties'].get('transcript', [])
            print("length of raw transcript", len(transcript))
            print("raw transcript   : ", transcript)
            raw_transcript_str = json.dumps(transcript)
            print("length of raw transcript", len(raw_transcript_str))

            print(f"Processing transcription for conversation {conversation_id}")

            # Prepare the output JSON structure
            interview_data = []
            current_entry = {"question": "", "visual_scene": "", "answer": ""}

            for entry in transcript:
                role = entry.get('role', '').lower()
                content = entry.get('content', '')
                visual_scene = extract_visual_scene(content)

                if role == "assistant":
                    # Append current entry if it's filled
                    if current_entry["question"] or current_entry["visual_scene"] or current_entry["answer"]:
                        interview_data.append(current_entry)
                    # Start a new question entry
                    current_entry = {
                        "question": clean_content(content),
                        "visual_scene": visual_scene,
                        "answer": ""
                    }
                elif role == "user":
                    # Add user's response as the answer to the current question
                    current_entry["answer"] = clean_content(content)
                    current_entry["visual_scene"] = visual_scene

            # Add the last entry if valid
            if current_entry["question"] or current_entry["visual_scene"] or current_entry["answer"]:
                interview_data.append(current_entry)

            if interview_data and not interview_data[0]["question"]:
                interview_data[0]["question"] = "Welcome in"

            # Save the structured data to output.json
            output_data = {"interview": interview_data}
            output_file = "output.json"
            with open(output_file, "w") as json_file:
                json.dump(output_data, json_file, indent=4)

            print(f"Transcription successfully processed and saved to {output_file}")
            save_transcription_to_database()
            return jsonify({"status": "Transcription processed successfully and saved to database!"}), 200
        else:
            return jsonify({"status": f"Unhandled event: {event_type}"}), 200

    except Exception as e:
        print(f"Error processing callback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500


def extract_visual_scene(content):
    """
    Extracts the 'VISUAL_SCENE:' information from the content string.
    """
    visual_scene = ""
    if "VISUAL_SCENE:" in content:
        try:
            visual_scene = content.split("VISUAL_SCENE:")[1].strip()
        except IndexError:
            visual_scene = ""
    return visual_scene


def clean_content(content):
    """
    Cleans the content string by removing unwanted prefixes like 'USER_SPEECH:' and 'VISUAL_SCENE:'.
    """
    cleaned = content
    if "USER_SPEECH:" in content:
        cleaned = content.split("USER_SPEECH:")[1].strip()
    if "VISUAL_SCENE:" in cleaned:
        cleaned = cleaned.split("VISUAL_SCENE:")[0].strip()
    return cleaned
