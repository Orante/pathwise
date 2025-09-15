import sys
from openai import OpenAI
from datetime import date
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.config import USER_DIR
from src.json_utils import add_goal
from src.chat_utils import ChatManagement
from src.ai_agents import GoalSettingAgent

# Set page config
st.set_page_config(
    page_title="Goal Setting Advisor",
    page_icon="🤖",
    layout="centered"
)

# Title
st.title("Goal Setting Advisor")

goals_chat = ChatManagement(
    session_key="goal_messages",
    initial_message="What goal do you have in mind?",
    system_message=f"Today's Date: {date.today()}.")

if "new_goal_info" not in st.session_state:
    st.session_state.new_goal_info = None

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

    # Clear chat button in sidebar
    if st.button("🗑️ Clear Chat"):
        goals_chat.clear()
        st.session_state.new_goal_info = None
        st.rerun()

goals_chat.display()

# User input
user_input = st.chat_input("Type your message here...")

# Handle user input and generate response
if user_input:
    # Add user message to chat history
    goals_chat.add_message("user", user_input)
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Generate AI response  
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Prepare messages for OpenAI API
            agent = GoalSettingAgent(
            )

            response = agent.generate_and_parse(
                api_key=API_KEY,
                messages=st.session_state.goal_messages
            )
            
            # Add AI response to chat history
            goals_chat.add_message("assistant", response["text"])
            st.session_state.new_goal_info = response["parsed"]

            st.write(response["parsed"])
            st.write(response["text"])

if st.button("Save Goal", icon="✅", type="secondary"):
    add_goal(user, st.session_state.new_goal_info)
    st.write("Saved!")