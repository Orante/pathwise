# pathfinder.py

from dotenv import load_dotenv, find_dotenv
import json
from openai import OpenAI
from pathlib import Path
import streamlit as st

from config.constants import *
from lib.tools_and_functions import *

### add a system message at the beginning containing

# Set page config
st.set_page_config(
    page_title="Pathwise Simulator",
    page_icon="🤖",
    layout="centered"
)

# Obtain user data
USERS_DIR = Path(__file__).resolve().parent.parent / "users_data"

def load_user_data(user):
    file_path = USERS_DIR / f"{user}.json"
    try:
        with open(file_path, "r") as f:
            return f.read()
    except:
        return {}

# Title
st.title("Pathwise Simulator 🛣️")

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
        [f"user_{i:05d}" for i in range(1, 6)],
        index=0
    )

    # Clear chat button in sidebar
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [{"role": "system", "content": f"Here is the user's information: {load_user_data(user)}"}]
        st.rerun()

# Initialize session state for messages and response_id
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": f"Here is the user's information: {load_user_data(user)}"}]

# Function to get AI response
def get_ai_response(messages,system_instructions, model):
    client = OpenAI(api_key = API_KEY)
    input_list = messages
    response = client.responses.create(
        model=model,
        input=input_list,
        instructions=system_instructions,
        tools = TOOLS,
    )
    print(f"{response.output}")
    print("\n\n\n")
    print(response)
    print("\n\n\n")

    while True:
        tool_result = []
        for item in response.output:
            if item.type == "function_call":
                function_call = item
                function_call_arguments = json.loads(item.arguments)

                func = FUNCTION_MAP.get(function_call.name)
                if func:
                    if func == save_user_data:
                        result = {function_call.name : save_user_data(messages,user)}
                    else:
                        result = {function_call.name : func(**function_call_arguments)}
                else:
                    result = f"Function {function_call.name} not found."
                print(result)

                tool_result.append({
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": json.dumps(result),
                })

        if not tool_result:
            return response.output_text
        
        input_list = messages + response.output + tool_result

        response = client.responses.create(
            model=model,
            input=input_list,
            instructions=system_instructions,
            tools = TOOLS,
        )
    
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
            output = get_ai_response(st.session_state.messages,INSTRUCTIONS,model)

            st.write(output)
        
    # Add AI response to chat history
    st.session_state.messages.append({"role": "assistant", "content": output})
    print(st.session_state.messages)