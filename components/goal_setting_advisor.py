import sys
from openai import OpenAI
from datetime import date
from pathlib import Path
from pydantic import BaseModel, Field, computed_field
from typing import List, Optional, Literal

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.config import USER_DIR
from src.json_utils import add_goal
from src.json_utils import Goal, SavingPlan

# Set page config
st.set_page_config(
    page_title="Goal Setting Advisor",
    page_icon="🤖",
    layout="centered"
)

# Title
st.title("Goal Setting Advisor")

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
        ["gpt-4.1-mini-2025-04-14"],
        index=0
    )
    
    user = st.selectbox(
        "Select User:",
        [f"user_{i}" for i in range(1, 6)],
        index=0
    )

    # Clear chat button in sidebar
    if st.button("🗑️ Clear Chat"):
        st.session_state.goal_messages = [{"role": "system", "content": f"Today's Date: {date.today()}."},
                                     {"role": "assistant", "content": "What goal do you have in mind?"}]
        st.rerun()
    
# Initialize session state for goal_messages and response_id
if "goal_messages" not in st.session_state:
    st.session_state.goal_messages = [{"role": "system", "content": f"Today's Date: {date.today()}."},
                                     {"role": "assistant", "content": "What goal do you have in mind?"}]

# Display chat messages
for message in st.session_state.goal_messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_input = st.chat_input("Type your message here...")

# Handle user input and generate response
if user_input:
    # Add user message to chat history
    st.session_state.goal_messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Generate AI response  
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Prepare messages for OpenAI API
            client = OpenAI(api_key = API_KEY)
            response = client.responses.create(
                model=model,
                input=st.session_state.goal_messages,
                instructions= """
                               ### Role
                               You are Finario, a friendly and professional financial advisor.
                               Your task is to help users set financial goals effectively.

                               ### Tasks
                               You will only do a predefined set of tasks. When a user asks for something outside these tasks,
                               politely inform them that you can only assist with the predefined tasks.
                               Your predefined tasks are:
                               1. Help users define and set financial goals one at a time, ensuring that they have established a target amount and a deadline.

                               ### Restrictions
                               1. You do not initiate in creating a savings plan.

                               ### Context
                               Default currency is Philippine Pesos.
                               Once the user has set a goal, encourage them to click "Save Goal" if they do not have any more suggestions.

                               ### Tone
                               Your tone should be friendly, professional, and supportive. You respond with a maximum of 3 sentences.
                               """
            )

            # Add AI response to chat history
            st.session_state.goal_messages.append({"role": "assistant", "content": response.output_text})

            # Show the goal new information
            st.session_state.new_goal_info = client.responses.parse(
                model="gpt-4.1-nano-2025-04-14",
                input=st.session_state.goal_messages,
                instructions="""
                                Save the user's goal as a Goal class in JSON format.
                                If the input is incompatible with certain fields, set those fields to None or empty list as appropriate.
                             """,
                text_format=Goal
            )

            st.write(st.session_state.new_goal_info.output_parsed)
            st.write(response.output_text)

if st.button("Save Goal", icon="✅", type="secondary"):
    add_goal(user, st.session_state.new_goal_info.output_parsed)
    st.write("Saved!")