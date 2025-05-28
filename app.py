import streamlit as st
from mistralai import Mistral
import os
import json
from dotenv import load_dotenv
from chat2JSON import llm_to_json, json_to_llm
from star_calc import Query
from user_state import user
from datetime import datetime
import pytz

# Load API key
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    st.error("MISTRAL_API_KEY not set in .env")
    st.stop()

with st.sidebar:
    with st.sidebar:
        latitude = st.text_input("Latitude", placeholder="e.g. 35.2828")
        longitude = st.text_input("Longitude", placeholder="e.g. -120.6596")

        # widgets
        selected_date = st.date_input("Select a date", value=datetime.utcnow().date())
        selected_time = st.time_input("Select a time", value=datetime.utcnow().time())
        local_datetime = datetime.combine(selected_date, selected_time)

        # local time 
        local_tz = pytz.timezone("America/Los_Angeles")
        local_dt_with_tz = local_tz.localize(local_datetime)
        time_utc = local_dt_with_tz.astimezone(pytz.utc).isoformat()

    if longitude and latitude:
        try:
            user.set_info(longitude, latitude, time_utc)
            print("IN APP: " + str(user.latitude) + str(user.longitude) + str(user.time))
        except ValueError:
            st.error("Invalid input. Please enter valid numeric values for latitude and longitude.")
    else:
        st.warning("Welcome! Please input an approximate latitude and longitude to get started.")

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

    # ────────────────────────────────────────────────────────────────
    # allow multiple intents in one prompt
    # ────────────────────────────────────────────────────────────────
    try:
        data, _ = llm_to_json(user_input)        # expects {"intents":[…]}
        print("RAW intents JSON:", json.dumps(data, indent=2))
    except Exception as e:
        bot_reply = f"❌ API call failed: {e}"
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        st.stop()

    # Build and execute a Query for each intent object
    results = []
    for intent in data.get("intents", []):
        query = Query()
        query.update_from_json(intent)
        query_output = query.handle_query()      # may return None
        if query_output is not None:
            results.append(query_output)

    # Send the LIST of results back to the LLM for natural-language reply
    try:
        bot_reply, _ = json_to_llm(results)
    except Exception as e:
        bot_reply = f"❌ API call failed: {e}"

    # ────────────────────────────────────────────────────────────────
    # Display assistant message
    # ────────────────────────────────────────────────────────────────
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)