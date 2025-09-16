import sys
from datetime import date, datetime
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

# # Run button to generate future paths
# if st.button("Generate Future Paths"):
#     agent = PathGeneratorAgent()
#     for col in st.columns(3):
#         response = agent.parse_response(
#             api_key=API_KEY,
#             messages=st.session_state.explore_paths_messages
#         )

#         explore_paths_chat.add_message("assistant", response.model_dump_json())

#         col.write(response.model_dump_json(indent = 2))


# Function to display goals within a timeline
def display_goal(goal: dict):
    # Calculate progress
    current_balance = goal.get("current_balance", 0.0)
    total_target = goal.get("total_target_amount", 1.0)
    progress = min(current_balance / total_target, 1.0)

    # Format deadline
    dl = goal["deadline"]
    if isinstance(dl, (datetime, date)):
        deadline = dl.strftime("%b %d, %Y")
    else:
        deadline = datetime.strptime(dl, "%Y-%m-%d").strftime("%b %d, %Y")
    
    # Status color
    status_colors = {
        "On Track": "✅",
        "Delayed": "⚠️"
    }
    status_icon = status_colors.get(goal["status"], "❓")
    
    st.markdown(f"**{goal['name']}** {status_icon}")
    st.progress(progress)
    st.markdown(f"- **Target:** PHP {total_target:,.2f}")
    st.markdown(f"- **Current:** PHP {current_balance:,.2f}")
    st.markdown(f"- **Deadline:** {deadline}")
    st.markdown(f"- **Flexibility:** {goal.get('flexibility', 'N/A')}")
    st.markdown(f"- **Priority:** {goal.get('priority', 'N/A')}")
    if goal.get("notes"):
        st.markdown(f"- **Notes:** {goal['notes']}")
    st.markdown("---")

def display_goal(goal: dict):
    # Calculate progress
    current_balance = goal.get("current_balance", 0.0)
    total_target = goal.get("total_target_amount", 1.0)
    progress = min(current_balance / total_target, 1.0)

    # Format deadline
    dl = goal.get("deadline")
    if dl:
        if isinstance(dl, (datetime, date)):
            deadline = dl.strftime("%b %d, %Y")
        else:
            try:
                deadline = datetime.strptime(dl, "%Y-%m-%d").strftime("%b %d, %Y")
            except Exception:
                deadline = str(dl)
    else:
        deadline = "No date provided"

    # Status color
    status_colors = {
        "On Track": "✅",
        "Delayed": "⚠️"
    }
    status_icon = status_colors.get(goal.get("status", ""), "❓")

    st.markdown(f"**{goal.get('name', 'Unnamed Goal')}** {status_icon}")
    st.progress(progress)
    st.markdown(f"- **Target:** PHP {total_target:,.2f}")
    st.markdown(f"- **Current:** PHP {current_balance:,.2f}")
    st.markdown(f"- **Deadline:** {deadline}")
    st.markdown(f"- **Flexibility:** {goal.get('flexibility', 'N/A')}")
    st.markdown(f"- **Priority:** {goal.get('priority', 'N/A')}")
    if goal.get("notes"):
        st.markdown(f"- **Notes:** {goal['notes']}")

    # Display saving plan (expandable)
    saving_plan = goal.get("saving_plan", [])
    if saving_plan:
        with st.expander("💰 View Saving Plan"):
            for plan in saving_plan:
                # Format start and end dates safely
                start = plan.get("start_date")
                end = plan.get("end_date")

                if start:
                    try:
                        start_str = datetime.strptime(start, "%Y-%m-%d").strftime("%b %d, %Y")
                    except Exception:
                        start_str = str(start)
                else:
                    start_str = "No date provided"

                if end:
                    try:
                        end_str = datetime.strptime(end, "%Y-%m-%d").strftime("%b %d, %Y")
                    except Exception:
                        end_str = str(end)
                else:
                    end_str = "No date provided"

                st.markdown(f"- **Period:** {start_str} → {end_str}")
                st.markdown(f"  - **Frequency:** {plan.get('saving_frequency', 'N/A')}")
                st.markdown(f"  - **Amount per Period:** PHP {plan.get('saving_amount_per_period', 0):,.2f}")
                st.markdown(f"  - **Target Amount:** PHP {plan.get('target_amount', 0):,.2f}")
                if plan.get("interest_rate"):
                    st.markdown(f"  - **Interest Rate:** {plan['interest_rate']}% ({plan.get('interest_frequency','N/A')})")

    st.markdown("---")

# Function to display a timeline with expanders for assumptions/resources
def display_timeline(timeline: dict):
    with st.container():
        st.markdown(f"## {timeline.get('title', 'Untitled Timeline')}")
        # Timeline risk
        risk_color = {
            "Healthy": "green",
            "Tight": "orange",
            "Critical": "red"
        }.get(timeline.get("timeline_risk"), "gray")
        
        st.markdown(
            f"**Timeline Risk:** <span style='color:{risk_color}'>{timeline.get('timeline_risk', 'N/A')}</span>", 
            unsafe_allow_html=True
        )

        # Resource Gaps
        if timeline.get("resource_gaps"):
            with st.expander("🛠️ Resource Gaps"):
                st.markdown(f"{timeline['resource_gaps']}")

        # Assumptions
        if timeline.get("assumptions"):
            with st.expander("📌 Assumptions"):
                for a in timeline["assumptions"]:
                    st.markdown(f"- {a}")

        # Goals
        st.markdown("### Goals")
        for goal in timeline.get("goals", []):
            display_goal(goal)

# --- Main UI ---

# After generating timelines with AI
if st.button("Generate Future Paths"):
    agent = PathGeneratorAgent()
    
    # Create 3 columns first
    cols = st.columns(3)
    
    for i in range(3):
        # Generate a single timeline
        response = agent.parse_response(
            api_key=API_KEY,
            messages=st.session_state.explore_paths_messages
        )
        timeline_dict = response.model_dump()
        
        # If response contains multiple timelines, just take the first
        if "timelines" in timeline_dict:
            timeline = timeline_dict["timelines"][0]
        else:
            timeline = timeline_dict
        
        # Display in the current column
        with cols[i % 3]:
            display_timeline(timeline)
