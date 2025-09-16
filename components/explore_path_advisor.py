import sys
from datetime import date
from pathlib import Path
import json

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.json_utils import load_user_file
from src.chat_utils import ChatManagement
from src.ai_agents import PathGeneratorAgent

# Set page config
st.set_page_config(
    page_title="Explore Path Advisor",
    page_icon="🤖",
    layout="centered"
)

# Title
st.title("Explore Path Advisor")

# Sidebar for API key input
with st.sidebar:
    st.header("Configuration")

    API_KEY = st.text_input(
        "Enter your OpenAI API Key:",
        type="password",
        placeholder="sk-..."
    )
    
    user = st.selectbox(
        "Select User:",
        [f"user_{i}" for i in range(1, 6)],
        index=0
    )

    user_data = load_user_file(user)

    explore_paths_chat = ChatManagement(
        session_key="explore_paths_messages",
        system_message=f"Today's Date: {date.today()}. Here is the user's information: {json.dumps(user_data)}"
    )

    # Clear chat button in sidebar
    if st.button("🗑️ Clear Chat"):
        explore_paths_chat.clear()
        st.rerun()

# Run button to generate future paths
if st.button("Generate Future Paths"):
    agent = PathGeneratorAgent()
    for col in st.columns(3):
        response = agent.parse_response(
            api_key=API_KEY,
            messages=st.session_state.explore_paths_messages
        )

        explore_paths_chat.add_message("assistant", response.model_dump_json())

        col.write(response.model_dump_json(indent = 2))
