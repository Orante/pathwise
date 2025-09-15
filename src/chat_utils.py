import streamlit as st
from typing import List, Dict

class ChatManagement:
    """Simple chat history manager"""
    
    def __init__(self, session_key: str = "messages", initial_message: str = None, system_message: str = None):
        self.session_key = session_key
        self.initial_message = initial_message
        self.system_message = system_message
        self._initialize()
    
    def _initialize(self):
        """Initialize chat history in session state"""
        if self.session_key not in st.session_state:
            messages = []
            if self.system_message:
                messages.append({"role": "system", "content": self.system_message})
            if self.initial_message:
                messages.append({"role": "assistant", "content": self.initial_message})
            st.session_state[self.session_key] = messages
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages"""
        return st.session_state[self.session_key]
    
    def add_message(self, role: str, content: str):
        """Add a message to history"""
        st.session_state[self.session_key].append({"role": role, "content": content})
    
    def clear(self):
        """Clear chat history"""
        messages = []
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})
        if self.initial_message:
            messages.append({"role": "assistant", "content": self.initial_message})
        st.session_state[self.session_key] = messages
    
    def display(self):
        """Display chat messages"""
        for message in st.session_state[self.session_key]:
            if message["role"] == "system":
                continue
            with st.chat_message(message["role"]):
                st.write(message["content"])