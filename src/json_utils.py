from datetime import date
from pydantic import BaseModel, Field, computed_field
from typing import List, Optional, Literal
import json
import uuid
import base64
from src.config import DATA_DIR

# List of all classes in this file:
class SavingPlan(BaseModel):
    """A plan to save towards a specific goal."""
    target_amount: float
    balance: Optional[float] = 0.0
    start_date: date
    end_date: date
    saving_frequency: Literal["daily", "bi-monthly", "monthly", "quarterly", "semi-annually", "annually"]
    saving_amount_per_period: float
    interest_rate: Optional[float] = 0.0
    interest_frequency: Optional[Literal["daily", "bi-monthly", "monthly", "quarterly", "semi-annually", "annually"]] = None

class Goal(BaseModel):
    name: str
    total_target_amount: float
    deadline: date
    saving_plan: List[SavingPlan] = Field(default_factory=list, description="A list of saving plans to achieve this goal. For example, you might have one plan to have 10000 monthly savings for the next 6 months, and another plan to have 5000 monthly savings for the following year.") 
    status: Literal["On Track","Delayed"]
    flexibility: Literal["Adjustable","Firm"]
    priority: Literal["High","Medium","Low"]
    created_at: date = Field(frozen = True, default_factory=date.today)         
    notes: str = Field(default=None, max_length=100, description="Additional notes about the goal that are not otherwise captured in the other fields.")

    @computed_field
    @property
    def current_balance(self) -> float:
        curr_balance = 0
        for plan in self.saving_plan:
            curr_balance += plan.balance
        return curr_balance

class Timeline(BaseModel):
    title: str = Field(description="Title of the timeline, e.g., 'Balanced Voyager', 'Risk Taker', 'Baby First'")
    goals: List[Goal] = Field(default_factory=list)
    timeline_risk: Literal["Healthy", "Tight", "Critical"]
    resource_gaps: str = Field(default=None, max_length=100)
    assumptions: List[str] = Field(default_factory=list)

class TimelineOptions(BaseModel):
    timelines: List[Timeline] = Field(min_length=3, max_length=3)
    
# Utility functions for user data management

def load_user_file(user_id):
    file_path = DATA_DIR / f"{user_id}.json"
    if file_path.exists():
        with open(file_path, "r") as f:
            return json.load(f)
    return {"user_id": user_id, "name": "", "goals": []}

def save_user_file(user_data):
    file_path = DATA_DIR / f"{user_data['user_id']}.json"
    with open(file_path, "w") as f:
        json.dump(user_data, f, indent=4)

def add_goal(user_id, goal_data):
    user_data = load_user_file(user_id)
    goal_data = goal_data.model_dump_json() # to solve non-serializable fields
    goal_data = json.loads(goal_data) # return to dict to combine with goal
    goal = {"id": str(uuid.uuid4())} | goal_data
    user_data["goals"].append(goal)
    save_user_file(user_data)
    return goal

def update_goal(user_id, goal_id, **kwargs):
    user_data = load_user_file(user_id)
    for goal in user_data["goals"]:
        if goal["id"] == goal_id:
            for key, value in kwargs.items():
                if key in goal:
                    goal[key] = value
            break
    save_user_file(user_data)

def delete_goal(user_id, goal_id):
    user_data = load_user_file(user_id)
    user_data["goals"] = [g for g in user_data["goals"] if g["id"] != goal_id]
    save_user_file(user_data)

def list_goals(user_id):
    user_data = load_user_file(user_id)
    return user_data["goals"]
