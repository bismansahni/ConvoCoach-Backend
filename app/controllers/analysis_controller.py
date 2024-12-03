from itertools import count

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

    #     prompt = (
    #         "For the given transcription of an interview, provide a detailed analysis by referring to the interviewee as you/yours to make the feedback sound natural and conversational like, include the following:\n"
    #         "1. Overall filler word count.\n"
    #         "2. Clarity score (on a scale of 0-10) and a reason for the score.\n"
    #         "3. Sentiment Analysis:\n"
    #         "   - Detect the overall tone (positive, neutral, negative).\n"
    #         "   - Provide feedback on emotional engagement.\n"
    #         "4. Response Length:\n"
    #         "   - Calculate the average and maximum response lengths.\n"
    #         "   - Provide feedback on whether the responses are concise, verbose, or balanced.\n"
    #         "5. Technical Depth:\n"
    #         "   - Assess relevance and depth of technical answers.\n"
    #         "   - Provide a technical score (on a scale of 0-10).\n"
    #         "6. Engagement Level:\n"
    #         "   - Analyze whether the interviewee asked questions or made follow-up comments.\n"
    #         "   - Provide an engagement score (on a scale of 0-10).\n"
    #         "7. Behavioral Questions Analysis:\n"
    #         "   - Evaluate adherence to the STAR format.\n"
    #         "   - Highlight strengths and weaknesses in storytelling.\n"
    #         "8. Time Management:\n"
    #         "   - Identify overly long or short answers.\n"
    #         "   - Provide feedback on time management.\n"
    #         "9. Grammar and Vocabulary:\n"
    #         "   - Assess the professionalism of language usage.\n"
    #         "   - Provide a grammar score (on a scale of 0-10).\n"
    #         "10. Confidence Level:\n"
    #         "    - Analyze confidence in tone and language.\n"
    #         "    - Provide a confidence score (on a scale of 0-10).\n"
    #         "11. Question Relevance:\n"
    #         "    - Evaluate how well responses address the question intent.\n"
    #         "    - Provide a relevance score (on a scale of 0-10).\n"
    #          "12. Summary:\n"
    #         "    - Highlight strengths and weaknesses.\n"
    #         "    - Provide actionable suggestions for improvement.\n\n"
    #         "13. Correctness Section:\n"
    #         "    - For individual questions and answers.\n"
    #         "   - Expected answer.\n"
    #          "   - Actual answer.\n"
    #          "   - Score for the answer (on a scale of 0-10).\n"
    #          "   - Reason for the score.\n"
    #
    #         "Try to elaborate the reason in detail and provide specific examples to support your point.\n"
    #         "The output should strictly follow this JSON format:\n"
    #         "{\n"
    #         '  "analysis": {\n'
    #         '    "filler_words_count": <int>,\n'
    #         '    "clarity_score": <int>,\n'
    #         '    "clarity_reason": "<string>",\n'
    #         '    "sentiment": {\n'
    #         '      "tone": "<positive|neutral|negative>",\n'
    #         '      "feedback": "<string>"\n'
    #         '    },\n'
    #         '    "response_length": {\n'
    #         '      "average_length": <int>,\n'
    #         '      "maximum_length": <int>,\n'
    #         '      "feedback": "<string>"\n'
    #         '    },\n'
    #         '    "technical_depth": {\n'
    #         '      "score": <int>,\n'
    #         '      "reason": "<string>"\n'
    #         '    },\n'
    #         '    "engagement_level": {\n'
    #         '      "score": <int>,\n'
    #         '      "feedback": "<string>"\n'
    #         '    },\n'
    #         '    "behavioral_questions": {\n'
    #         '      "strength": "<string>",\n'
    #         '      "weakness": "<string>",\n'
    #         '      "feedback": "<string>"\n'
    #         '    },\n'
    #         '    "time_management": {\n'
    #         '      "score": <int>,\n'
    #         '      "feedback": "<string>"\n'
    #         '    },\n'
    #         '    "grammar_and_vocabulary": {\n'
    #         '      "score": <int>,\n'
    #         '      "feedback": "<string>"\n'
    #         '    },\n'
    #         '    "confidence_level": {\n'
    #         '      "score": <int>,\n'
    #         '      "feedback": "<string>"\n'
    #         '    },\n'
    #         '    "question_relevance": {\n'
    #         '      "score": <int>,\n'
    #         '      "feedback": "<string>"\n'
    #         '    },\n'
    #         '    "summary": {\n'
    #         '      "strengths": "<string>",\n'
    #         '      "weaknesses": "<string>",\n'
    #         '      "suggestions": "<string>"\n'
    #         '    }\n'
    #        '    "correctness": [\n'
    # '      {\n'
    # '        "question": "<string>",\n'
    # '        "expected_answer": "<string>",\n'
    # '        "actual_answer": "<string>",\n'
    # '        "score": <int>,\n'
    # '        "reason": "<string>"\n'
    # '      }\n'
    # '    ]\n'
    # "  }\n"
    # "}\n"
    # "\n"
    # "Here is the transcription for analysis:\n"
    # f"{transcription}"
    #     )

        prompt = (
            "For the given transcription of an interview, provide a detailed analysis by referring to the interviewee as you/yours to make the feedback sound natural and conversational. Include the following:\n"
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
            "    - Provide actionable suggestions for improvement.\n"
            "13. Correctness Section:\n"
            "    - Analyze every single individual question and answer. Do not omit any question or answer keep the transcript as it is. For every individual question give: \n"
            "    - Expected answer.\n"
            "    - Actual answer.\n"
            "    - Score for the answer (on a scale of 0-10).\n"
            "    - Reason for the score.\n"
            "\n"
            "Try to elaborate the reason in detail and provide specific examples to support your point.\n"
            "The output should strictly follow this JSON format without any additional text before or after the JSON object. The response must only contain the JSON object as plain text.\n"
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
            '    },\n'
            '    "correctness": [\n'
            '      {\n'
            '        "question": "<string>",\n'
            '        "expected_answer": "<string>",\n'
            '        "actual_answer": "<string>",\n'
            '        "score": <int>,\n'
            '        "reason": "<string>"\n'
            '      }\n'
            '    ]\n'
            "  }\n"
            "}\n"
            "\n"
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
        analysis_data = json.loads(cleaned_response)["analysis"]

        # # Save the analysis data to Firestore
        # analysis_ref = db.collection("users").document(uid).collection("interviewDetails").document(interview_doc_id).collection("analysis").collection("ai_feedback")
        # analysis_doc_ref = analysis_ref.document("feedback")
        # analysis_doc_ref.set(analysis_data)

        analysis_ref = db.collection("users").document(uid).collection("interviewDetails").document(interview_doc_id).collection("analysis").document("ai_feedback")
        analysis_ref.set(analysis_data)

        update_overall_metrics(analysis_data, uid, interview_doc_id)

        print("Analysis metrics added to Firestore successfully!")
    except Exception as e:
        print(f"Error cleaning analysis metrics: {traceback.format_exc()}")
        return {"error": str(e)}, 500

#
# def update_overall_metrics(analysis_data, uid, interview_doc_id):
#     try:
#         # Fetch the user document
#         user_ref = db.collection('users').document(uid)
#         user_doc = user_ref.get()
#
#         if "overall_metrics" in user_doc.to_dict():
#             overall_metrics = user_doc.to_dict()["overall_metrics"]
#             interview_count = overall_metrics["interview_count"]
#
#             # Increment the interview count
#             interview_count += 1
#
#             # Update metrics
#             overall_metrics["filler_words_count"] = (
#                 (overall_metrics["filler_words_count"] * (interview_count - 1)) +
#                 analysis_data["filler_words_count"]
#             ) / interview_count
#             overall_metrics["clarity_score"] = (
#                 (overall_metrics["clarity_score"] * (interview_count - 1)) +
#                 analysis_data["clarity_score"]
#             ) / interview_count
#             overall_metrics["response_length"] = {
#                 "average_length": (
#                     (overall_metrics["response_length"]["average_length"] * (interview_count - 1)) +
#                     analysis_data["response_length"]["average_length"]
#                 ) / interview_count,
#                 "maximum_length": max(
#                     overall_metrics["response_length"]["maximum_length"],
#                     analysis_data["response_length"]["maximum_length"]
#                 )
#
#             }
#
#             # Update only `score` from specific metrics
#             for key in [
#                 "technical_depth",
#                 "engagement_level",
#                 "time_management",
#                 "grammar_and_vocabulary",
#                 "confidence_level",
#                 "question_relevance"
#             ]:
#                 overall_metrics[key] = (
#                     (overall_metrics[key] * (interview_count - 1)) +
#                     analysis_data[key]["score"]
#                 ) / interview_count
#
#             overall_metrics["interview_count"] = interview_count
#
#         else:
#             # Initialize overall metrics for the first interview
#             overall_metrics = {
#                 "filler_words_count": analysis_data["filler_words_count"],
#                 "clarity_score": analysis_data["clarity_score"],
#                 "response_length": analysis_data["response_length"],
#                 "technical_depth": analysis_data["technical_depth"]["score"],
#                 "engagement_level": analysis_data["engagement_level"]["score"],
#                 "time_management": analysis_data["time_management"]["score"],
#                 "grammar_and_vocabulary": analysis_data["grammar_and_vocabulary"]["score"],
#                 "confidence_level": analysis_data["confidence_level"]["score"],
#                 "question_relevance": analysis_data["question_relevance"]["score"],
#                 "interview_count": 1
#             }
#
#         # Update the user document with the overall metrics
#         user_ref.update({"overall_metrics": overall_metrics})
#
#         print("Overall metrics updated successfully!")
#     except Exception as e:
#         print(f"Error updating overall metrics: {traceback.format_exc()}")
#         return {"error": str(e)}, 500






def update_overall_metrics(analysis_data, uid, interview_doc_id):
    try:
        # Reference to the user's overall_metrics collection
        metrics_ref = db.collection('users').document(uid).collection('overall_metrics')
        metrics_doc = metrics_ref.document('metrics_summary').get()

        if metrics_doc.exists:
            overall_metrics = metrics_doc.to_dict()
            interview_count = overall_metrics["interview_count"]

            # Increment the interview count
            interview_count += 1

            # Update metrics
            overall_metrics["filler_words_count"] = (
                (overall_metrics["filler_words_count"] * (interview_count - 1)) +
                analysis_data["filler_words_count"]
            ) / interview_count
            overall_metrics["clarity_score"] = (
                (overall_metrics["clarity_score"] * (interview_count - 1)) +
                analysis_data["clarity_score"]
            ) / interview_count
            overall_metrics["response_length"] = {
                "average_length": (
                    (overall_metrics["response_length"]["average_length"] * (interview_count - 1)) +
                    analysis_data["response_length"]["average_length"]
                ) / interview_count,
                "maximum_length": max(
                    overall_metrics["response_length"]["maximum_length"],
                    analysis_data["response_length"]["maximum_length"]
                )
            }

            # Update only `score` from specific metrics
            for key in [
                "technical_depth",
                "engagement_level",
                "time_management",
                "grammar_and_vocabulary",
                "confidence_level",
                "question_relevance"
            ]:
                overall_metrics[key] = (
                    (overall_metrics[key] * (interview_count - 1)) +
                    analysis_data[key]["score"]
                ) / interview_count

            overall_metrics["interview_count"] = interview_count

        else:
            # Initialize overall metrics for the first interview
            overall_metrics = {
                "filler_words_count": analysis_data["filler_words_count"],
                "clarity_score": analysis_data["clarity_score"],
                 "response_length": {
                    "average_length": analysis_data["response_length"]["average_length"],
                    "maximum_length": analysis_data["response_length"]["maximum_length"]
                },
                "technical_depth": analysis_data["technical_depth"]["score"],
                "engagement_level": analysis_data["engagement_level"]["score"],
                "time_management": analysis_data["time_management"]["score"],
                "grammar_and_vocabulary": analysis_data["grammar_and_vocabulary"]["score"],
                "confidence_level": analysis_data["confidence_level"]["score"],
                "question_relevance": analysis_data["question_relevance"]["score"],
                "interview_count": 1
            }

        # Save or update the overall metrics in the collection
        metrics_ref.document('metrics_summary').set(overall_metrics)

        print("Overall metrics updated successfully in the collection!")
    except Exception as e:
        print(f"Error updating overall metrics: {traceback.format_exc()}")
        return {"error": str(e)}, 500
