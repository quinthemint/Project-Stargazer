import streamlit as st

st.title("🔭 Stargazer Chat (Prototype)")

# Initialize session state for conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input field
user_input = st.chat_input("Ask about stars, planets, or constellations...")

if user_input:
    # Show user's message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Placeholder/dummy response (for now)
    placeholder_response = f"🛰️ Placeholder: I'm thinking about your question: _'{user_input}'_..."

    # Show bot message
    st.session_state.messages.append({"role": "assistant", "content": placeholder_response})
    with st.chat_message("assistant"):
        st.markdown(placeholder_response)
