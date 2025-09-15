import sys
from openai import OpenAI
from datetime import date
from pathlib import Path
from pydantic import BaseModel, Field, computed_field
from typing import List, Optional, Literal
import json

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.config import USER_DIR
from src.json_utils import load_user_file

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
    
    model = st.selectbox(
        "Select Model:",
        ["gpt-4.1-mini-2025-04-14","gpt-5-mini", "gpt-5", "gpt-5-nano"],
        index=0
    )
    
    user = st.selectbox(
        "Select User:",
        [f"user_{i}" for i in range(1, 6)],
        index=0
    )

    user_data = load_user_file(user)

    # Clear chat button in sidebar
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [{"role": "system", "content": f"Here is the user's information: {user_data}"}]
        st.rerun()

if "explore_paths_messages" not in st.session_state:
    st.session_state.explore_paths_messages = [{"role": "system", "content": f"Today's Date: {date.today()}."},
                                               {"role": "system", "content": f"Here is the user's information: {json.dumps(user_data)}"}]

# Run button to generate future paths
if st.button("Generate Future Paths"):
    client = OpenAI(api_key=API_KEY)

    for col in st.columns(3):
        response = client.responses.parse(
            model=model,
            input=st.session_state.explore_paths_messages,
            instructions=
            """
            ### Role
            You are an expert financial advisor specializing in creating personalized financial plans that help users achieve their goals.
            ### Task
            Develop a distinct future financial paths for the user based on their profile and goals. Each should include a detailed saving plan.
            ### Context
            The currency is in Philippine pesos, unless stated otherwise.
            """,
            tools = [{
                "type": "code_interpreter",
                "container": {"type": "auto"}
            }],
        )
        st.session_state.explore_paths_messages.append({"role": "assistant", "content": response.output_text})
        col.write(response.output_text)
