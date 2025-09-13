from openai import OpenAI
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import date

# List of all tools
FUNCTION_CALLINGS = [
    {
    "type": "function",
    "name": "save_user_data",
    "description": "Save the user's financial record for Pathwise in a structured JSON file. "
            "This record must include user profile, assumptions, and timeline (goals + life events). "
            "Ensure concise_additional_notes are always short and to the point. "
            "Used for record-keeping so the user does not need to re-enter information for future simulations.",
    "parameters": {
            "type": "object",
            "properties": {}
    },
    }
]

# List of all classes
class Goal(BaseModel):
    name: str
    target_amount: float
    current_savings: Optional[float] = 0.0   # Progress toward goal
    deadline: date
    monthly_saving_required: Optional[float] = None
    status: Optional[str] = None             # e.g., "on track", "delayed"
    created_at: Optional[str] = None         # YYYY-MM-DD
    last_updated: Optional[str] = None       # YYYY-MM-DD
    notes: Optional[str] = None


class LifeEvent(BaseModel):
    type: str
    description: Optional[str] = None
    impact: Optional[str] = None
    date: Optional[str] = None               # YYYY-MM
    status: Optional[str] = None             # e.g., "simulated", "confirmed"
    resolved: Optional[bool] = None
    concise_additional_notes: Optional[str] = None


class UserProfile(BaseModel):
    id: str
    name: str
    age: Optional[int] = None
    status: Optional[str] = None
    dependents: Optional[int] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    risk_tolerance: Optional[str] = None
    profile_last_updated: Optional[str] = None
    concise_additional_notes: Optional[str] = None


class Assumptions(BaseModel):
    inflation_rate: Optional[float] = 0.05
    safe_return_rate: Optional[float] = 0.06
    moderate_return_rate: Optional[float] = 0.10
    aggressive_return_rate: Optional[float] = 0.14
    emergency_fund_months: Optional[int] = 6


class InvestmentAccount(BaseModel):
    name: str
    balance: float
    estimated_interest_rate: float = 0.0     # Annual %, 0 if no interest
    type: Optional[str] = None               # e.g., "emergency fund", "stocks"
    risk_level: Optional[str] = None         # safe / moderate / aggressive
    last_updated: Optional[str] = None       # YYYY-MM-DD
    concise_additional_notes: Optional[str] = None


class Loan(BaseModel):
    name: str
    balance: float
    interest_rate: float                     # Annual %
    monthly_payment: Optional[float] = None
    deadline: Optional[str] = None           # YYYY-MM if applicable
    status: Optional[str] = None             # e.g., "active", "paid off"
    last_updated: Optional[str] = None       # YYYY-MM-DD
    concise_additional_notes: Optional[str] = None


class SavingsAndInvestments(BaseModel):
    accounts: List[InvestmentAccount]
    loans: List[Loan]


class Timeline(BaseModel):
    goals: List[Goal]
    life_events: List[LifeEvent]


class PathwiseRecord(BaseModel):
    user: UserProfile
    assumptions: Assumptions
    timeline: Timeline
    savings_and_investments: SavingsAndInvestments
    last_updated: str   # YYYY-MM-DD



# List of all fucntions
def save_user_data(conversation,user_id):
    """
    Save user data from an AI conversation into a JSON file.

    This function sends the conversation to the OpenAI model, requesting that it 
    return the user's data in a structured format (`PathwiseRecord`). The parsed output 
    is then saved to a JSON file in the specified directory. Each user gets a 
    file named "user_<user_id>.json".

    Returns:
        str: Confirmation message indicating that the user data was successfully saved.
    """

    DIR = Path("./users_data")

    client = OpenAI()
    collected_user_data = client.responses.parse(
        model="gpt-5-mini",
        input=conversation,
        text_format= PathwiseRecord
    )

    output = collected_user_data.output_parsed

    file_path = DIR / f"{user_id}.json"
    with open(file_path, "w") as f:
        f.write(output.model_dump_json(indent=2))

    return "Successfully saved user data."

TOOLS = FUNCTION_CALLINGS + [{
            "type": "code_interpreter",
            "container": {"type": "auto"}
        }]

FUNCTION_MAP = {
    "save_user_data": save_user_data
    # Add more functions here as needed
    # We will include a functino where an AI outputs a JSON formatting using Structured Output
}