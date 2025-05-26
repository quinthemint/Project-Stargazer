import os
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise RuntimeError("Missing MISTRAL_API_KEY in .env")
client = Mistral(api_key=api_key)
MODEL  = "mistral-large-latest" # model selection

# Define a helper that always returns JSON + usage
def llm_to_json(user_prompt: str, **chat_kwargs):
    messages = [
        {
            "role": "system",
            "content": """You are a JSON generator.
            The user will give an input for you to turn into optional keys that will be only Constellation, Star, ASKCONVIS, ASKSTAVIS, ASKSTAPAR, ASKCONCHI.
            ASKCONVIS will be a 1 if they ask about the visibility of a constellation. ASKSTAVIS will be a 1 if they ask about the visibility of a star. 
            ASKSTAPAR will be a 1 if they ask about the constellation a star belongs to. ASKCONCHI will be a 1 if they ask about the stars in a constellation. You may set 
            multiple fields to 1 if you are unsure of user intent. Always include all fields; any field not set to 1 is set to 0""",
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    time.sleep(1.1) # important, this prevents exceeding rate limit

    response = client.chat.complete(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"},   #KEY LINE
        **chat_kwargs,
    )

    # The SDK guarantees valid JSON when that flag is set
    data  = json.loads(response.choices[0].message.content)
    usage = response.usage                      # prompt_tokens
    return data, usage

# instructs llm to turn json with output info into natural language
def json_to_llm(data: dict, **chat_kwargs):
    messages = [
        {
            "role": "system",
            "content": """You are a formatter that turns structured JSON data about stars into clear, natural language.
            Explain whether the star is visible, where it is (altitude and azimuth), and what constellation it belongs to if the
            respective information is provided. Avoid repeating field names or JSON terms in the output — 
            just speak like a knowledgeable astronomy assistant.
            """,
        },
        {
            "role": "user",
            "content": json.dumps(data, indent=2),
        },
    ]

    response = client.chat.complete(
        model=MODEL,
        messages=messages,
        **chat_kwargs,
    )

    return response.choices[0].message.content, response.usage