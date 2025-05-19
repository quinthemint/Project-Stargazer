import streamlit as st
from mistralai import Mistral
import os
import json
from dotenv import load_dotenv
from chat2JSON import llm_to_json
# from star_calc import 

# Load API key
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    st.error("MISTRAL_API_KEY not set in .env")
    st.stop()

with st.sidebar:
    longitude = st.text_input("Longitude", placeholder="e.g. -122.4194")
    latitude = st.text_input("Latitude", placeholder="e.g. 37.7749")
    time_utc = st.text_input("UTC Time", placeholder="YYYY-MM-DD or full ISO")

print(longitude + "\n")
print(latitude + "\n")
print(time_utc + "\n")

# Initialize Mistral client
client = Mistral(api_key=api_key)

st.title("🔭 Stargazer Chat (Prototype)")

# Initialize conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Ask about stars, planets, or constellations...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        data, _ = llm_to_json(user_input)
        bot_reply = f"Parsed intent:\n```json\n{json.dumps(data, indent=2)}\n```"
    except Exception as e:
        bot_reply = f"❌ API call failed: {e}"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)