import json
import requests
from typing import Optional
import streamlit as st
from langflow.load import load_flow_from_json

# Load the flow from the JSON file
flow_data = json.load(open("LifeLift.json"))
flow_id = flow_data.get("id", "")

BASE_API_URL = "http://127.0.0.1:7860/api/v1/run"
FLOW_ID = flow_id
ENDPOINT = ""  # You can set a specific endpoint name in the flow settings

# Extract TWEAKS from the JSON file
TWEAKS = {node["id"]: {} for node in flow_data.get("data", {}).get("nodes", [])}

def run_flow(message: str,
             endpoint: str,
             output_type: str = "chat",
             input_type: str = "chat",
             tweaks: Optional[dict] = None,
             api_key: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.
    """
    api_url = f"{BASE_API_URL}/{endpoint}"
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if api_key:
        headers = {"x-api-key": api_key}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

st.set_page_config(page_title="LifeLift Health Coach", page_icon="🏋️‍♀️", layout="wide")
st.title("🏋️‍♀️ LifeLift Health Coach")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("How can I help you with your health and wellness today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            response = run_flow(
                message=prompt,
                endpoint=FLOW_ID,
                output_type="chat",
                input_type="chat",
                tweaks=TWEAKS
            )
            
            if "output" in response:
                full_response = response["output"]
            else:
                full_response = "I'm sorry, I couldn't generate a response. Could you please try rephrasing your question?"

        except Exception as e:
            full_response = f"An error occurred: {str(e)}"

        message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar with health tips
st.sidebar.title("Quick Health Tips")
st.sidebar.info(
    "1. Stay hydrated: Drink at least 8 glasses of water daily.\n"
    "2. Get moving: Aim for 30 minutes of exercise most days.\n"
    "3. Eat a balanced diet: Include fruits, vegetables, and whole grains.\n"
    "4. Prioritize sleep: Aim for 7-9 hours of quality sleep each night.\n"
    "5. Manage stress: Practice relaxation techniques like deep breathing or meditation."
)

# Footer
st.markdown("---")
st.markdown("LifeLift Health Coach - Your AI partner for better health and wellness.")