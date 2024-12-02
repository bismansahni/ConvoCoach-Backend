import firebase_admin
from firebase_admin import credentials, firestore
import traceback, os
import json
from app.controllers.firebase_config import db
import openai
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("API_KEY")

openai.api_key = api_key

def save_transcription_to_database():
    try:
        # Load candidate data from JSON
        with open("candidate-data.json", "r") as file:
            candidate_data = json.load(file)

        uid = candidate_data["uid"]
        interview_doc_id = candidate_data["interviewDocId"]

        # Read the transcription from the file
        with open("output.json", "r") as file:
            transcription = json.load(file)

        # Initialize Firebase Admin SDK
        # if not firebase_admin._apps:
        #     cred = credentials.Certificate("service-key.json")
        #     firebase_admin.initialize_app(cred)
        #
        # db = firestore.client()

        # Define the document reference in Firestore
        analysis_ref = db.collection("users").document(uid).collection("interviewDetails").document(interview_doc_id).collection("analysis")

        # Add the transcription under an "analysis" field
        # analysis_doc = {
        #     "transcription": transcription
        #    # Optional timestamp field
        # }
        # analysis_collection_ref.add(analysis_doc)

        transcription_doc_ref = analysis_ref.document("transcription")
        transcription_doc_ref.set({"transcription": transcription})
        print("Transcription added to 'analysis' collection successfully!")
        create_analysis_metrics(transcription, uid, interview_doc_id)
    except Exception as e:
        print(f"Error uploading transcription: {traceback.format_exc()}")
        return {"error": str(e)}, 500

#
# def create_analysis_metrics(transcription):
#     response = openai.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages
#     )
#
#     prompt: for the given transcription which is of an interview, give me overall filler word count, clarity score,and overall reason, and for indivudal conversation messages,  as



def create_analysis_metrics(transcription, uid, interview_doc_id):
    try:
        # Construct the prompt
        # prompt = (
        #     "For the given transcription of an interview, provide the following:\n"
        #     "1. Overall filler word count.\n"
        #     "2. Clarity score (on a scale of 0-10) and a reason for the score.\n"
        #     "3. For individual questions and answers:\n"
        #     "   - Expected answer.\n"
        #     "   - Actual answer.\n"
        #     "   - Score for the answer (on a scale of 0-10).\n"
        #     "   - Reason for the score.\n"
        #     " Use 'you' or 'your' to make the feedback sound direct and conversational.\n"
        #
        #     "The output should strictly follow this JSON format:\n"
        #     "{\n"
        #     '  "analysis": {\n'
        #     '    "filler_words_count": <int>,\n'
        #     '    "clarity_score": <int>,\n'
        #     '    "reason": "<string>",\n'
        #     '    "correctness": [\n'
        #     "      {\n"
        #     '        "question": "<string>",\n'
        #     '        "expected_answer": "<string>",\n'
        #     '        "actual_answer": "<string>",\n'
        #     '        "score": <int>,\n'
        #     '        "reason": "<string>"\n'
        #     "      }\n"
        #     "    ]\n"
        #     "  }\n"
        #     "}\n"
        #     "Also calculate the average score of all answers as (sum of all scores / number of questions)."
        #     "Here is the transcription:\n"
        #     f"{transcription}"
        # )

        prompt = (
            "For the given transcription of an interview, provide a detailed analysis by referring to the interviewee as you/yours to make the feedback sound natural and conversational like, include the following:\n"
            "1. Overall filler word count.\n"
            "2. Clarity score (on a scale of 0-10) and a reason for the score.\n"
            "3. Sentiment Analysis:\n"
            "   - Detect the overall tone (positive, neutral, negative).\n"
            "   - Provide feedback on emotional engagement.\n"
            "4. Response Length:\n"
            "   - Calculate the average and maximum response lengths.\n"
            "   - Provide feedback on whether the responses are concise, verbose, or balanced.\n"
            "5. Technical Depth:\n"
            "   - Assess relevance and depth of technical answers.\n"
            "   - Provide a technical score (on a scale of 0-10).\n"
            "6. Engagement Level:\n"
            "   - Analyze whether the interviewee asked questions or made follow-up comments.\n"
            "   - Provide an engagement score (on a scale of 0-10).\n"
            "7. Behavioral Questions Analysis:\n"
            "   - Evaluate adherence to the STAR format.\n"
            "   - Highlight strengths and weaknesses in storytelling.\n"
            "8. Time Management:\n"
            "   - Identify overly long or short answers.\n"
            "   - Provide feedback on time management.\n"
            "9. Grammar and Vocabulary:\n"
            "   - Assess the professionalism of language usage.\n"
            "   - Provide a grammar score (on a scale of 0-10).\n"
            "10. Confidence Level:\n"
            "    - Analyze confidence in tone and language.\n"
            "    - Provide a confidence score (on a scale of 0-10).\n"
            "11. Question Relevance:\n"
            "    - Evaluate how well responses address the question intent.\n"
            "    - Provide a relevance score (on a scale of 0-10).\n"
            "12. Summary:\n"
            "    - Highlight strengths and weaknesses.\n"
            "    - Provide actionable suggestions for improvement.\n\n"
            "Try to elaborate the reason in detail and provide specific examples to support your point.\n"
            "The output should strictly follow this JSON format:\n"
            "{\n"
            '  "analysis": {\n'
            '    "filler_words_count": <int>,\n'
            '    "clarity_score": <int>,\n'
            '    "clarity_reason": "<string>",\n'
            '    "sentiment": {\n'
            '      "tone": "<positive|neutral|negative>",\n'
            '      "feedback": "<string>"\n'
            '    },\n'
            '    "response_length": {\n'
            '      "average_length": <int>,\n'
            '      "maximum_length": <int>,\n'
            '      "feedback": "<string>"\n'
            '    },\n'
            '    "technical_depth": {\n'
            '      "score": <int>,\n'
            '      "reason": "<string>"\n'
            '    },\n'
            '    "engagement_level": {\n'
            '      "score": <int>,\n'
            '      "feedback": "<string>"\n'
            '    },\n'
            '    "behavioral_questions": {\n'
            '      "strength": "<string>",\n'
            '      "weakness": "<string>",\n'
            '      "feedback": "<string>"\n'
            '    },\n'
            '    "time_management": {\n'
            '      "score": <int>,\n'
            '      "feedback": "<string>"\n'
            '    },\n'
            '    "grammar_and_vocabulary": {\n'
            '      "score": <int>,\n'
            '      "feedback": "<string>"\n'
            '    },\n'
            '    "confidence_level": {\n'
            '      "score": <int>,\n'
            '      "feedback": "<string>"\n'
            '    },\n'
            '    "question_relevance": {\n'
            '      "score": <int>,\n'
            '      "feedback": "<string>"\n'
            '    },\n'
            '    "summary": {\n'
            '      "strengths": "<string>",\n'
            '      "weaknesses": "<string>",\n'
            '      "suggestions": "<string>"\n'
            '    }\n'
            "  }\n"
            "}\n\n"
            "Here is the transcription for analysis:\n"
            f"{transcription}"
        )

        # Prepare messages for OpenAI API
        messages = [
            {"role": "system", "content": "You are an assistant trained to analyze interviews."},
            {"role": "user", "content": prompt}
        ]

        response = openai.chat.completions.create(
             model="gpt-4o-mini",
            messages=messages
        )

        ai_response =  response.choices[0].message.content
        clean_metrics(ai_response, uid, interview_doc_id)
        print("Analysis Metrics:\n", ai_response)

    except Exception as e:
        print(f"Error generating analysis metrics: {traceback.format_exc()}")
        return {"error": str(e)}, 500


def clean_metrics(ai_response, uid, interview_doc_id):
    try:
        cleaned_response = ai_response.replace("```json", "").replace("```", "").strip()
        # Parse the AI response JSON
        analysis_data = json.loads(ai_response)["analysis"]

        # # Save the analysis data to Firestore
        # analysis_ref = db.collection("users").document(uid).collection("interviewDetails").document(interview_doc_id).collection("analysis").collection("ai_feedback")
        # analysis_doc_ref = analysis_ref.document("feedback")
        # analysis_doc_ref.set(analysis_data)

        analysis_ref = db.collection("users").document(uid).collection("interviewDetails").document(interview_doc_id).collection("analysis").document("ai_feedback")
        analysis_ref.set(analysis_data)

        print("Analysis metrics added to Firestore successfully!")
    except Exception as e:
        print(f"Error cleaning analysis metrics: {traceback.format_exc()}")
        return {"error": str(e)}, 500
