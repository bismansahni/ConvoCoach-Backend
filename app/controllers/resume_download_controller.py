

import json
import os
import firebase_admin
from firebase_admin import credentials, storage
import PyPDF2
from dotenv import load_dotenv
import openai


load_dotenv()
api_key = os.getenv("API_KEY")

# Initialize OpenAI with the API key
openai.api_key = api_key


# Initialize Firebase with your service account credentials
# cred = credentials.Certificate("service-key.json")
# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'ai-interviewer-9aeea.appspot.com'
# })
#
# bucket = storage.bucket()

if not firebase_admin._apps:
    cred = credentials.Certificate("service-key.json")  # Path to your service account file
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'ai-interviewer-9aeea.appspot.com'  # Your Firebase Storage bucket name
    })

# Firebase Storage bucket
bucket = storage.bucket()

def get_persona_data():
    # Read 'candidate-data.json' to extract candidate data
    with open('candidate-data.json', 'r') as file:
        data = json.load(file)

    # Extracting necessary fields from candidate data
    uid = data.get('uid')
    interviewDocId=data.get('interviewDocId')
    resumepath=[uid,interviewDocId]
    print("interviewDocId received:",interviewDocId) # UID will be used for downloading the resume
    return resumepath





def download_resume():
    try:
        # Extract UID from persona data
        resumepath = get_persona_data()
        uid = resumepath[0]
        interviewDocId=resumepath[1]


        # if not uid:
        #     print("UID not found in the JSON file.")
        #     return

        # Construct the Firebase Storage path using the UID
        firebase_path = f'resumes/{uid}/{interviewDocId}/resume.pdf'
        blob = bucket.blob(firebase_path)

        # Download the file to a local path
        local_filename = 'candidate-resume.pdf'
        blob.download_to_filename(local_filename)

        print('File downloaded successfully!')
        extract_summary()

    except FileNotFoundError:
        print("candidate-data.json file not found.")
    except Exception as e:
        print(f'Error: {e}')






def extract_summary():
    resume_path = 'candidate-resume.pdf'
    output_path = 'candidateinfo.txt'
    #  Open the PDF file
    with open(resume_path, "rb") as file:
    # Initialize the PDF reader
        reader = PyPDF2.PdfReader(file)
    
    # Extract text from each page
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()

    with open(output_path, "w") as text_file:
        text_file.write(text)
    # Print or process the extracted text
        # print(text)
    extract_questions()


def extract_questions():
    candidateinfo_path = 'candidateinfo.txt'
    output_path = 'questions.txt'

    with open(candidateinfo_path, "r") as file:
        text = file.read()

    messages = [
        {
            "role": "user",
            "content": (
                # f"You are {interviewer_name}, a {interviewer_role} at {company}. "
                # f"You are preparing to interview {candidate_name} for the {role} position. "
                "The following is the candidate's resume summary.Generate four questions relevant for the interview based on  the candidate's experience and skills. Ask specific questions about the candidate's experience and skills."
                "Just give the questions back, nothing else in the response."
            )
        },
        {
            "role": "user",
            "content": text
        }
    ]


    

    # Make the request to OpenAI to summarize and generate questions
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Extract the response content
    ai_response =  response.choices[0].message.content

    with open(output_path, "w") as file:
        file.write(ai_response)

    # print(ai_response)  # Print the AI's response
    return ai_response


  
    






