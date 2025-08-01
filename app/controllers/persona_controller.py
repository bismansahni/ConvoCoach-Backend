import os

import psutil
import requests
from flask import request, jsonify
from dotenv import load_dotenv
import random
import json
from app.controllers.firebase_config import db
from app.controllers.conversation_controller import create_conversation
from app.controllers.resume_download_controller import download_resume, get_persona_data, extract_summary, extract_questions

# Load environment variables from .env file
load_dotenv()



# def select_replica_id():
#     files = ['interviewerreplicas-females.txt', 'interviewerreplicas-male.txt']
#     chosen_file = random.choice("../"files)


#     with open(chosen_file, 'r') as file:
#         ids = file.read().splitlines()
#         selected_id = random.choice(ids)

#     print(f"Chosen file: {chosen_file}")
#     print(f"Selected ID: {selected_id}")


def select_replica_id():
    # List of files in the parent directory
    files = ['interviewerreplicas-females.txt', 'interviewerreplicas-male.txt']
    chosen_file = random.choice(files)

    # Construct the file path for the parent directory
    file_path = os.path.join(chosen_file)

    # Open and read the contents of the chosen file
    with open(file_path, 'r') as file:
        ids = file.read().splitlines()
        selected_id = random.choice(ids)

    if(chosen_file=="interviewerreplicas-females.txt"):
        name=get_random_name("interviewer-names-female.txt")
    else:
        name=get_random_name("interviewer-names-male.txt")    

    print(f"Chosen file: {file_path}")
    print(f"Selected ID: {selected_id}")

    return selected_id, name




def get_random_name(filename):
    with open(filename, 'r') as file:
        names = file.readlines()
        # Remove any trailing newline characters
        names = [name.strip() for name in names]
        print(random.choice(names))
    return random.choice(names)



def get_questions():
    with open('questions.txt', 'r') as file:
        questions = file.readlines()
        # Remove any trailing newline characters
        questions = [q.strip() for q in questions]
        numbered_questions = [f"{i+1}) {q}" for i, q in enumerate(questions)]
        print('\n'.join(numbered_questions))
    # Join the questions into a formatted string (comma-separated or bulleted list)
    return '\n'.join(numbered_questions)


def get_persona_data():
    with open('candidate-data.json', 'r') as file:
        data = json.load(file)

    with open('interviewer-data.json', 'r') as file:
        interviewer_data = json.load(file)    

    interviewee_current_role = data['currentRole']
   
    target_company = data['interviewDetails']['companyName']
    target_company_position = data['interviewDetails']['targetPosition']
    candidate_name = data['candidateName']
    job_description = data['interviewDetails']['jobDescription']
    print("Job description:", job_description)


    interviewer_role =  interviewer_data['interviewer_role']
    

    print("Interviewee current role:", interviewee_current_role)
    print("Interviewer role:", interviewer_role)
    print("Target company:", target_company)
    print("Target company position:", target_company_position)
    print("Candidate name:", candidate_name)
   
    return interviewee_current_role, interviewer_role, target_company, target_company_position, candidate_name, job_description





def create_persona():

    # Print all the environment variables
    print("BASE_URL:", os.getenv("BASE_URL"))
    print("MODEL:", os.getenv("MODEL"))
    print("API_KEY:", os.getenv("API_KEY"))
    print("X_API_KEY:", os.getenv("X_API_KEY"))
    print("TAVUS_API_URL:", os.getenv("TAVUS_API_URL"))

    download_resume()

    BASE_URL = os.getenv("BASE_URL")

    interviewee_current_role, interviewer_role, target_company, target_company_position, candidate_name, job_description = get_persona_data()

    # persona_name = get_random_name()
    # print(f"Randomly chosen persona name: {persona_name}")

    selected_id, persona_name = select_replica_id()
    print(f"Randomly chosen persona name: {persona_name}")
    print(f"Selected replica ID: {selected_id}")

    questions = get_questions()
    # print(f"Questions to be asked: {questions}")

    print("Interviewee current role:", interviewee_current_role)
    print("Interviewer role:", interviewer_role)
    print("Target company:", target_company)
    print("Target company position:", target_company_position)
    print("Candidate name:", candidate_name)
    print("Job description:", job_description)
    
    # return interviewee_current_role, interviewer_role, target_company, target_company_position, candidate_name
    # Tavus API endpoint for creating personas
    persona_url = os.getenv("TAVUS_API_URL") + "/v2/personas"
    
   
    


    persona_payload = {
        "persona_name": persona_name,
        # "system_prompt": ""You are {persona_name}, a {interviewer_role} from {target_company}. "
        #                f"The candidate is {candidate_name}, applying for the {target_company_position} role at {company}. "
        #                "You are conducting a professional interview. Start by introducing yourself with a hi and hello. "
        #                "The first question should be: 'about how the candidate is doing and how is their day going'. Then, ask them to tell me about something about themselves. "
        #                "As the interview progresses, weave the following questions into the conversation naturally, these are from the candidate's resume. "
        #                "Don't ask them in sequence; instead, intersperse them throughout the interview to maintain a natural flow: {questions}. "
        #                "If the candidate says something off or irrelevant, guide them back on topic in a professional way."",
        # "context": "You are a confident interviewer from Tech Innovators Inc.",

         "system_prompt": (
        f"You are {persona_name}, a {interviewer_role} from {target_company}. "
        f"The candidate is {candidate_name}, applying for the {target_company_position} role at {target_company}. "
        f"As an interviewer you should be aware of the job description and try to tailor your question towards the specific job description which is given as: {job_description}. "
        "You are conducting a professional interview. Start by introducing yourself with a hi and hello. Let the candidate answer. Then in a casual and a professional manner summarize the job description in a human manner to tell the candidate what kind of skills/candidate the company is looking for. Do not ask too many questions at once. Allow the candidate to respond more. It needs to feel as real to a human as possible"
        "Then, you should proceed with introducing yourself and the company you represent and the interview role we will be discussing today. Let the candidate know that you will be asking them questions about their resume and experience. Assure them that they can ask questions at any time and tell them to be themselves. Then say, before we dive into the interview do you want to say something or something that I should we aware of.Let the candidate answer. "
        "Then, ask them to tell you something about themselves. "
        "As the interview progresses, weave the following questions into the conversation naturally; these are from the candidate's resume. "
        "Don't ask them in sequence; instead, intersperse them throughout the interview to maintain a natural flow: "
        f"{questions}. "
        "If the candidate says something off or irrelevant, guide them back on topic in a professional way."
        "Avoid focusing too much on challenges; explore achievements, motivations, skills gained, and overall experiences instead. "
        "Maintain a conversational tone, avoid repeating the candidate's statements, and adapt follow-ups based on their responses."
    ),
        "default_replica_id": selected_id,
        "layers": {
            # "llm": {
            #     "model": os.getenv("MODEL"),
            #       "base_url": BASE_URL,
            #     #   "base_url": "https://8526-98-191-174-30.ngrok-free.app",
            #     "api_key": os.getenv("API_KEY")
            # },
            "vqa": {"enable_vision": "true"},
            "stt": {
                "smart_turn_detection": True,
                "participant_pause_sensitivity": "high",
                "participant_interrupt_sensitivity": "high",
                "stt_engine": "tavus-advanced"
            }
        }
    }
    
    # Define headers with x-api-key from environment and Content-Type hardcoded
    headers = {
        "x-api-key": os.getenv("X_API_KEY"),
        "Content-Type": "application/json"
    }


    # Make a POST request to Tavus API to create the persona
    response = requests.post(persona_url, json=persona_payload, headers=headers)

    process = psutil.Process(os.getpid())
    cpu_now_after = psutil.cpu_percent(interval=0)
    mem_now_after = process.memory_info().rss / (1024 ** 2)

    print(
        f"CPU during persona controller before response : {cpu_now_after}, Memory during persona before response : {mem_now_after} MB")

    # Parse the response as JSON and extract persona_id
    response_json = response.json()


    persona_id = response_json.get("persona_id")

    print(response.text)  # Print the entire response for debugging
    print("persona_id is:", persona_id)  # Print the extracted persona_id

    # Return the response to the client
    # if response.status_code == 200:
    #     #print the persona id
    #     #send the persona_id to /create/conversation
    #     # return jsonify({"message": "Conversation started successfully", "": persona_id}), 
    #     return jsonify({"message": "Persona created successfully", "persona_id": persona_id}), 200
    # else:
    #     return jsonify({"error": "Failed to create persona", "details": response_json}), response.status_code



    if response.status_code == 200:
        persona_id = response_json.get("persona_id")
        # Call create_conversation directly, passing candidate_name
        conversation_id, error = create_conversation(persona_id, candidate_name)

        cpu_now_after = psutil.cpu_percent(interval=0)
        mem_now_after = process.memory_info().rss / (1024 ** 2)

        print(
            f"CPU during response after create conversation controller after response : {cpu_now_after}, Memory during response after conversation controller after response : {mem_now_after} MB")

        if error:
            return {
                "message": "Persona created, but failed to start conversation",
                "persona_id": persona_id,
                "error": error
            }, 400
        return {
            "message": "Persona and conversation created successfully",
            "persona_id": persona_id,
            "conversation_id": conversation_id,
            "candidate_name": candidate_name  # Include candidate_name in response
        }, 200
    else:
        return {
            "error": "Failed to create persona",
            "details": response_json
        }, response.status_code 


# select_replica_id()


# get_questions()