# import openai
# from dotenv import load_dotenv
# import os
#
# # Load environment variables
# load_dotenv()
#
# # Set OpenAI API key
# api_key = os.getenv("API_KEY")
# if not api_key:
#     raise ValueError("API key not found. Ensure it is set in your .env file.")
#
# openai.api_key = api_key
#
# def transcription_formatter():
#     # Read transcription from file
#     try:
#         with open("transcription.txt", "r") as file:
#             transcription = file.read()
#     except FileNotFoundError:
#         raise FileNotFoundError("The file 'transcription.txt' was not found.")
#
#     # Define prompt
#     prompt = (
#         "This is a transcription of an interview, however it is not in a good and presentable format. "
#         "I want you to give me a nice and formatted transcript in JSON format (as I am building a backend API "
#         "to access the whole interview). There should be an array of questions and answers. "
#         "For every question the interviewer asked, write the EXACT VISUAL_SCENE as the transcript gives, "
#         "do not make any changes. Provide it in JSON format."
#     )
#
#     sampleresponse={{
#   "interview": [
#     {
#       "question": "Hi Vihaan! It’s great to meet you. I’m Charlotte, the Hiring Manager here at Iced Hazelnut Latte. We’re excited to discuss the SDE1 intern role with you today. This position focuses on skills in React, TypeScript, and Node.js, so we’re really looking for someone who is comfortable with building dynamic user interfaces and has a good grasp of backend development as well. I’ll be asking about your resume and any experiences you’d like to share. Feel free to ask questions at any time and just be yourself. Before we dive in, is there anything you’d like to share or something I should be aware of?",
#       "visual_scene": "The image shows a person wearing glasses and a red head covering, sitting indoors. The background includes a ceiling with lights and some wall decorations.",
#       "answer": "Hi, how are you?"
#     },
#     {
#       "response": "I'm doing well, thanks for asking! It's nice to see you smiling. So, can you tell me a bit about yourself and your background?",
#       "visual_scene": "The image shows a person wearing glasses and a red head covering, smiling at the camera. The background appears to be an indoor setting with a ceiling light and some wall decorations.",
#       "answer": "So I'm currently a computer science junior and I have extensive experience in everything which you so desire and I can come and like give you a nice coffee as well."
#     },
#     {
#       "question": "That's great to hear! It sounds like you have a strong background. We're definitely looking for someone with hands-on experience, especially in React, TypeScript, and Node.js. Could you share a specific challenge you faced while developing responsive UI components for NAB Solutions and how you overcame it to ensure cross-platform compatibility?",
#       "visual_scene": "The image shows a person smiling, wearing glasses and a red head covering. They are in an indoor setting with a ceiling light and some framed pictures or maps on the wall behind them.",
#       "answer": "So what I did was I was like drinking a lot of coffee all the time. So coffee actually helped me do a lot of stuff. So that was one of the important aspects for what what do you think?"
#     },
#     {
#       "response": "I can appreciate the power of coffee—it's a great motivator! However, let's focus a bit on your experiences. Can you tell me about a specific challenge you faced while developing those UI components? What strategies did you use to tackle cross-platform compatibility?",
#       "visual_scene": "The image shows a person wearing glasses and a red patterned head covering, sitting in an indoor setting. The background includes a ceiling with lights, a map on the wall, and an exit sign.",
#       "answer": "Sorry, I'm sorry to interrupt you. I just wanted to know what company I'm actually interviewing for."
#     },
#     {
#       "response": "No problem at all! You're interviewing for a SDE1 intern role at Iced Hazelnut Latte. We focus on creating engaging applications, and we're looking for someone who can contribute to our projects using React, TypeScript, and Node.js. Does that help clarify things? If you have any other questions, feel free to ask!",
#       "visual_scene": "The image shows two people in an indoor setting, possibly a room or office. One person is wearing a red head covering and glasses, while the other is wearing a striped shirt. The background includes some wall art and a ceiling with lights.",
#       "answer": "Actually, it does not clarify anything, and I would like more clarification. And I actually just don't like you as my interviewer, I'd like to have someone else."
#     },
#     {
#       "response": "I appreciate your honesty, Vihaan. I'm here to make sure you have a positive experience, and it's important that you're comfortable. Let me clarify a bit more: Iced Hazelnut Latte is focused on creating innovative applications that enhance our user experience, and the SDE1 intern role will involve working closely with our development team to build and maintain these applications. If you'd prefer to talk to someone else, I can certainly arrange that, but I'd love to continue our conversation if you're willing. What specific information are you looking for?",
#       "visual_scene": "The image shows a person wearing glasses and a red head covering with a checkered pattern. They are smiling and appear to be in an indoor setting, possibly an office or classroom, with maps on the wall in the background.",
#       "answer": "Are you single by any chance I'm going to take you on a date?"
#     },
#     {
#       "response": "I appreciate the compliment, but let's keep our focus on the interview and the role. I'm here to discuss your qualifications and experiences related to the SDE1 intern position. So, how about sharing more about your time as a UGTA for the iOS App Development course? How did you measure the effectiveness of the MapKit lab you developed?",
#       "visual_scene": "The image shows a person wearing glasses and a red patterned head covering, sitting in an indoor setting. The background includes a ceiling with lights, a map on the wall, and some office furniture.",
#       "answer": "No, I really, really like you."
#     },
#     {
#       "response": "Thank you for your kind words, Vihaan! It’s always nice to hear that. However, I want to make sure we're focusing on the interview and your fit for the position. Can you tell me more about your cohesive UI/UX strategy at Medical Directive? I'm interested in how you used tools like Figma and Canva to enhance user satisfaction.",
#       "visual_scene": "The image shows a person wearing glasses and a red head covering, sitting in a room with a ceiling light. There are maps or posters on the wall behind them, and the room appears to be an office or study space.",
#       "answer": "I just."
#     },
#     {
#       "response": "[INTERRUPTED]",
#       "visual_scene": "The image shows a person wearing glasses and a red head covering, smiling. They are indoors, with maps on the wall behind them and a ceiling with lights.",
#       "answer": "I just do not talk to you. It's all good. Thank you. We are done."
#     },
#     {
#       "response": "I understand, Vihaan. Thank you for your time today! If you have any thoughts or feedback in the future, feel free to reach out. Best of luck with your endeavors!",
#       "visual_scene": "The image shows a person wearing glasses and a red head covering, smiling at the camera. They are in an indoor setting with maps on the wall and a ceiling with lights."
#     }
#   ]
# }
# }
#
#     # Prepare messages for the OpenAI API
#     messages = [
#         {"role": "user", "content": prompt},
#         {"role": "user", "content": transcription}
#     ]
#
#     # Call OpenAI's chat completion endpoint
#     try:
#         response = openai.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=messages,
#             max_tokens=1500,
#             temperature=0.7
#         )
#         ai_response = response.choices[0].message.content
#         print("AI Response:", ai_response)
#     except openai.error.OpenAIError as e:
#         raise RuntimeError(f"An error occurred while calling the OpenAI API: {e}")
#
#     return ai_response
#
#
# transcription_formatter()
import json

import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set OpenAI API key
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API key not found. Ensure it is set in your .env file.")

openai.api_key = api_key


def transcription_formatter():
    # Read transcription from file
    try:
        with open("transcription.txt", "r") as file:
            transcription = file.read()
    except FileNotFoundError:
        raise FileNotFoundError("The file 'transcription.txt' was not found.")

    sampleresponse = {
        "interview": [
            {
                "question": "Hi Vihaan! It’s great to meet you. I’m Charlotte, the Hiring Manager here at Iced Hazelnut Latte. We’re excited to discuss the SDE1 intern role with you today...",
                "visual_scene": "The image shows a person wearing glasses and a red head covering, sitting indoors...",
                "answer": "Hi, how are you?"
            },
            {
                "response": "I'm doing well, thanks for asking! It's nice to see you smiling...",
                "visual_scene": "The image shows a person wearing glasses and a red head covering, smiling at the camera...",
                "answer": "So I'm currently a computer science junior..."
            }

        ]
    }

    sample_response_str = json.dumps(sampleresponse, indent=4)

    # Define prompt
    prompt = (
        "This is a transcription of an interview, however it is not in a good and presentable format. "
        "I want you to give me a nice and formatted transcript in JSON format with the following structure:"
        f"{sample_response_str}\n\n"
        "For every question the interviewer asked, write the EXACT VISUAL_SCENE as the transcript gives, "
        "Do not make any changes to the transcription and provide the full conversation."
        "Do not add any additional information to the transcript as the transcript is real conversation between two people, you do not have to change anything in the transcript."
    )

    # Sample response for reference


    # print("Sample Response for reference:\n", sampleresponse)

    print("getting it!")

    # Prepare messages for the OpenAI API
    messages = [
        {"role": "user", "content": prompt},
        {"role": "user", "content": transcription}
    ]

    # Call OpenAI's chat completion endpoint
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            # max_tokens=1500,
            # temperature=0.7
        )
        ai_response = response.choices[0].message.content

        # Attempt to parse the response as JSON
        # try:
        #     parsed_response = json.loads(ai_response)
        # except json.JSONDecodeError:
        #     # Fix formatting if the response is not valid JSON
        #     print("Fixing invalid JSON formatting...")
        #     ai_response = (
        #         ai_response.replace("'''", "")  # Remove triple quotes if present
        #         .replace("“", '"').replace("”", '"')  # Normalize double quotes
        #         .replace("’", "'")  # Normalize single quotes
        #     )
        #     parsed_response = json.loads(ai_response)  # Reattempt parsing
        #
        # # Save the fixed JSON to a file
        # output_file = "transcript-updated-response.json"
        # with open(output_file, "w") as file:
        #     json.dump(parsed_response, file, indent=4)
        # print(f"AI Response saved to {output_file} successfully!")



        output_file = "transcript-updated-response.txt"
        with open(output_file, "w") as file:
            file.write(ai_response)

        print(f"AI Response saved to {output_file} successfully!")

    except openai.error.OpenAIError as e:
        raise RuntimeError(f"An error occurred while calling the OpenAI API: {e}")

    clean_transcript_file("transcript-updated-response.txt","output.json")
    return ai_response


def clean_transcript_file(file_path, output_json_file):
    """
    Cleans the transcript file by removing the first line if it is ```json
    and the last line if it is ```, then saves the cleaned content into a JSON file.

    :param file_path: Path to the transcript file.
    :param output_json_file: Path to save the cleaned content as a JSON file.
    """
    try:
        # Read the file content
        with open(file_path, "r") as file:
            lines = file.readlines()

        # Check and remove the first line if it matches ```json
        if lines and lines[0].strip() == "```json":
            lines = lines[1:]

        # Check and remove the last line if it matches ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        # Join the lines back to a single string
        cleaned_content = "".join(lines)

        # Parse the cleaned content as JSON
        try:
            parsed_json = json.loads(cleaned_content)

            # Save the parsed JSON to the specified output file
            with open(output_json_file, "w") as json_file:
                json.dump(parsed_json, json_file, indent=4)

            print(f"Cleaned JSON content successfully saved to '{output_json_file}'!")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON content: {e}")
            return

        print(f"File '{file_path}' has been updated and cleaned successfully!")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Run the transcription_formatter function
# transcription_formatter()
