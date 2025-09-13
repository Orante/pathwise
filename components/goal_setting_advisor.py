from openai import OpenAI
from datetime import date
from pathlib import Path
from pydantic import BaseModel, computed_field
from typing import List, Optional, Literal

import streamlit as st

# List of all classes in this file:
class SavingPlan(BaseModel):
    target_amount: float
    balance: Optional[float] = 0.0
    start_date: date
    end_date: date
    interest_rate: Optional[float] = 0.0
    interest_frequency: Optional[Literal["daily", "bi-monthly", "monthly", "quarterly", "semi-annually", "annually"]] = None

class Goal(BaseModel):
    name: str
    total_target_amount: float
    deadline: date
    saving_plan: Optional[List[SavingPlan]] = []
    status: Literal["On Track","Delayed"]
    flexibility: Literal["Adjustable","Firm"]
    priority: Literal["High","Medium","Low"]
    created_at: Optional[str] = None         
    notes: Optional[str] = None

    @computed_field
    @property
    def current_balance(self) -> float:
        curr_balance = 0
        for plan in self.saving_plan:
            curr_balance += plan.balance
        return curr_balance

# Obtain user data
USERS_DIR = Path(__file__).resolve().parent.parent / "users_data"

def load_user_data(user):
    file_path = USERS_DIR / f"{user}.json"
    try:
        with open(file_path, "r") as f:
            return f.read()
    except:
        return {}

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
        ["gpt-4.1-mini-2025-04-14","gpt-5-mini", "gpt-5", "gpt-5-nano"],
        index=0
    )
    
    user = st.selectbox(
        "Select User:",
        [f"user_{i}" for i in range(1, 6)],
        index=0
    )

    # Clear chat button in sidebar
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [{"role": "system", "content": f"Here is the user's information: {load_user_data(user)}"},
                                     {"role": "assistant", "content": "What goal do you have in mind?"}]
        st.rerun()

# Initialize session state for messages and response_id
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": f"Here is the user's information: {load_user_data(user)}"},
                                     {"role": "assistant", "content": "What goal do you have in mind?"}]

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_input = st.chat_input("Type your message here...")

# Handle user input and generate response
if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
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
                input=st.session_state.messages,
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

            st.write(response.output_text)
        
    # Add AI response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response.output_text})

