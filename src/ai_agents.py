import streamlit as st
from openai import OpenAI
from typing import Optional, List, Type
from dataclasses import dataclass
from pydantic import BaseModel
from src.json_utils import Goal, Timeline

@dataclass
class AgentConfig:
    """Configuration for AI agents"""
    api_key: Optional[str] = None
    model: str = "gpt-4.1-mini-2025-04-14"
    instructions: str = ""
    parse_instructions: Optional[str] = None
    tools: Optional[List[dict]] = None
    parse_model: Optional[str] = None
    text_format: Optional[Type[BaseModel]] = None
    

class AIAgent:
    """Simple AI Agent class"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
    
    def _create_client(self, api_key: str) -> OpenAI:
        """Create OpenAI client"""
        return OpenAI(api_key=api_key)
    
    def generate_response(self, api_key: str, messages) -> str:
        """Generate a simple text response"""
        client = self._create_client(api_key)
        
        response = client.responses.create(
            model=self.config.model,
            input=messages,
            instructions=self.config.instructions,
            tools=self.config.tools
        )
        
        return response.output_text
    
    def parse_response(self, api_key: str, messages) -> BaseModel:
        """Parse response into Pydantic model"""
        if not self.config.text_format:
            raise ValueError("text_format must be set for parsing")
        
        client = self._create_client(api_key)
        
        parse_model = self.config.parse_model or self.config.model
        parse_instructions = self.config.parse_instructions or self.config.instructions
        
        response = client.responses.parse(
            model=parse_model,
            input=messages,
            instructions=parse_instructions,
            text_format=self.config.text_format
        )
        
        return response.output_parsed
    
    def generate_and_parse(self, api_key: str, messages) -> dict:
        """Generate response and parse it"""
        client = self._create_client(api_key)
        
        # Generate response
        response = client.responses.create(
            model=self.config.model,
            input=messages,
            instructions=self.config.instructions,
            tools=self.config.tools
        )
        
        result = {"text": response.output_text}
        
        # Parse if format is provided
        if self.config.text_format:
            parse_model = self.config.parse_model or self.config.model
            parse_instructions = self.config.parse_instructions or self.config.instructions
            
            parsed_response = client.responses.parse(
                model=parse_model,
                input=messages + [{"role": "assistant", "content": response.output_text}],
                instructions=parse_instructions,
                text_format=self.config.text_format
            )
            
            result["parsed"] = parsed_response.output_parsed
        
        return result


class GoalSettingAgent(AIAgent):
    """Agent for goal setting conversations"""
    
    def __init__(self):
        instructions = """
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
        
        parse_instructions = """
        Save the user's goal as a Goal class in JSON format.
        If the input is incompatible with certain fields, set those fields to None or empty list as appropriate.
        """

        parse_model = "gpt-4.1-nano-2025-04-14"

        text_format = Goal
        
        config = AgentConfig(
            instructions=instructions,
            parse_instructions=parse_instructions,
            parse_model=parse_model,
            text_format=text_format,
        )
        super().__init__(config)

class PathGeneratorAgent(AIAgent):
    """Agent for generating future financial paths"""
    
    def __init__(self):
        instructions = """
        ### Role
        You are an expert financial advisor specializing in creating personalized financial plans that help users achieve their goals.
        
        ### Task
        Develop a *DIFFERENT* future financial path option for the user based on their profile and goals. Each path should include:
        1. A *DIFFERENT* concise, creative, and descriptive title.
        2. A *DIFFERENT* set of saving plans for EACH goal. Each saving plan contains at least a deadline, target amount, saving frequency, and saving amount per period.
        
        ### Context
        The currency is in Philippine pesos, unless stated otherwise.
        """
        
        tools = [{
            "type": "code_interpreter",
            "container": {"type": "auto"}
        }]

        text_format = Timeline
        
        config = AgentConfig(
            instructions=instructions,
            tools=tools,
            text_format=text_format
        )
        super().__init__(config)