import os
import json
from pathlib import Path

from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise RuntimeError("Missing MISTRAL_API_KEY in .env")
client = Mistral(api_key=api_key)
MODEL  = "mistral-large-latest"             # change if you prefer

# Define a helper that always returns JSON + usage
def llm_to_json(user_prompt: str, **chat_kwargs):
    messages = [
        {
            "role": "system",
            "content": "You are a JSON generator.",
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

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


if __name__ == "__main__":
    prompt = """The user will give an input for you to turn into optional keys that will be only Constellation, Star. 
    In that order. Since this is optional, the alternative would be 0. The USER says: 
    Where is the star Ax207b?"""

    try:
        payload, usage = llm_to_json(prompt)
    except Exception as e:
        print("LLM call failed:", e)
        raise

    # Save prettified JSON
    out_path = Path("output.json")
    out_path.write_text(json.dumps(payload, indent=2))
    print(f"Saved JSON to {out_path}")
    print(
        f"Usage: prompt={usage.prompt_tokens}, "
        f"completion={usage.completion_tokens}, total={usage.total_tokens}"
    )
