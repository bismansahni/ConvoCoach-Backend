import os

import psutil
import requests
from dotenv import load_dotenv
from flask import Flask, Response, request, stream_with_context
# Load environment variables from .env file
# load_dotenv()
import time



from openai import OpenAI

import traceback
import json
from flask import Blueprint, jsonify

print("BASE_URL:", os.getenv("BASE_URL"))
base_url=os.getenv("BASE_URL")

conversation_bp = Blueprint('conversation_bp', __name__)

def create_conversation(persona_id,candidate_name):
    conversation_url = os.getenv("TAVUS_API_URL") + "/v2/conversations"
    conversation_payload = {
        # "replica_id": "r1fbfc941b",
        "persona_id": persona_id,
         "callback_url": f"{base_url}/callback",
        "conversation_name": "Dave- Interviewer",
        # "conversational_context": (
        #     f"You are the interviewer with persona ID {persona_id}. "
        #     "You are conducting a professional interview."
        # ),
          "custom_greeting": "Welcome in.",
        "properties": {
            "max_call_duration": 600,
            "participant_left_timeout": 50,
        }
    }

    headers = {
        "x-api-key": os.getenv("X_API_KEY"),
        "Content-Type": "application/json"
    }

    # Make a POST request to create the conversation
    response = requests.post(conversation_url, json=conversation_payload, headers=headers)

    process = psutil.Process(os.getpid())
    cpu_now_after = psutil.cpu_percent(interval=0)
    mem_now_after = process.memory_info().rss / (1024 ** 2)

    print(f"CPU during conversation controller before response : {cpu_now_after}, Memory during conversation before response : {mem_now_after} MB")
    response_json = response.json()

    print("hi. we are somewhere")


    # response = requests.request("POST", conversation_url, json=conversation_payload, headers=headers)
    # print(response.text)

    # process = psutil.Process(os.getpid())
    cpu_now_after = psutil.cpu_percent(interval=0)
    mem_now_after = process.memory_info().rss / (1024 ** 2)

    print(
        f"CPU during conversation controller after response : {cpu_now_after}, Memory during conversation after response : {mem_now_after} MB")


    print("hi. we are somewhere")

    if response.status_code == 200:
        conversation_id = response_json.get("conversation_id")
        conversation_url = response_json.get("conversation_url")
        print("hi. we are somewhere again")
        return (conversation_id,conversation_url), None  # Success, return conversation_id
    else:
        print("response_json",response_json)
        return None, response_json  # Failure, return error details


