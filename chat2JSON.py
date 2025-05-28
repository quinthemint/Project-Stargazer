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
            "content": """
            You are a JSON generator.
            **Output format**  
            Return ONE top-level JSON object with exactly one key: **"intents"**.  
            That key maps to an ARRAY.  Each element of the array is an **intent
            object** describing a single user request.

            **Fields inside every intent object**

            | Field          | Type   | Meaning                                                     |
            |----------------|--------|-------------------------------------------------------------|
            | "Constellation"| string | Name of the constellation the user mentioned, lowercase; empty string "" if not applicable. |
            | "Star"         | string | Common name of the star mentioned, lowercase; empty string "" if not applicable. |
            | "ASKCONVIS"    | 0 or 1 | 1 → user asks about the VISIBILITY of a constellation.      |
            | "ASKSTAVIS"    | 0 or 1 | 1 → user asks about the VISIBILITY of a star.               |
            | "ASKSTAPAR"    | 0 or 1 | 1 → user asks **which constellation** a star belongs to.    |
            | "ASKCONCHI"    | 0 or 1 | 1 → user asks for the **stars contained in** a constellation. |

            Include **all six fields** in every intent.  
            Set a flag to 1 when you are confident OR uncertain it applies; set to 0 when it clearly does not.

            **Multiple questions in one sentence**  
            If the user's input contains several separate questions relating to more than one object (star/constellation), create **one
            intent object per related object**, in the order they appear, and place them
            all inside the "intents" array.

            **Constraints**
            * The top level MUST be: `{ "intents": [ {...}, {...}, ... ] }`
            """
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