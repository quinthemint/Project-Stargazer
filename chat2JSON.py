import os
import json
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise RuntimeError("Set MISTRAL_API_KEY in your .env")

#Instantiate client
client = Mistral(api_key=api_key)

messages = [
    {"role": "system",  "content": "You are a JSON generator."},
    {"role": "user",    "content": "Turn this into a JSON object: Describe a red car with fields make, model, year."}
]

# Call the chat endpoint
response = client.chat.complete(
    model="mistral-large-latest",
    messages=messages,
)

# Extract the model’s text
raw = response.choices[0].message.content

# Parse it as JSON
try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    print("XXX Failed to parse JSON:", e)
    print("Model output:")
    print(raw)
    exit(1)

with open("output.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Saved JSON to output.json")
