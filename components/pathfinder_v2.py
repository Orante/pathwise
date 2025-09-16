import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Pathfinder",
    page_icon="🎯",
    layout="wide"
)

# Initialize session state
if 'show_ai_chat' not in st.session_state:
    st.session_state.show_ai_chat = False
if 'show_future_paths' not in st.session_state:
    st.session_state.show_future_paths = False
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'ai_input' not in st.session_state:
    st.session_state.ai_input = ""

# Sample goals data
sample_goals = [
    {
        "title": "Learn Python Programming",
        "description": "Master Python fundamentals and advanced concepts",
        "progress": 65,
        "category": "Education"
    },
    {
        "title": "Launch Side Business",
        "description": "Create and launch a profitable online business",
        "progress": 30,
        "category": "Business"
    },
    {
        "title": "Improve Physical Health",
        "description": "Establish consistent exercise routine and healthy diet",
        "progress": 80,
        "category": "Health"
    },
    {
        "title": "Read 24 Books This Year",
        "description": "Expand knowledge through consistent reading habits",
        "progress": 50,
        "category": "Personal"
    },
    {
        "title": "Build Professional Network",
        "description": "Connect with industry professionals and mentors",
        "progress": 25,
        "category": "Career"
    }
]

# Header
st.title("🎯 Pathfinder")
st.markdown("Track your goals and explore future possibilities")

# Goals Section
st.header("Your Goals")

# Display limited number of goals (4 in this case)
goals_to_show = 4
cols = st.columns(2)

for i, goal in enumerate(sample_goals[:goals_to_show]):
    with cols[i % 2]:
        with st.container():
            st.markdown(f"""
            <div style="
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                background-color: #fafafa;
            ">
                <h4 style="margin-bottom: 10px; color: #333;">{goal['title']}</h4>
                <p style="color: #666; margin-bottom: 15px;">{goal['description']}</p>
                <div style="margin-bottom: 10px;">
                    <span style="background-color: #e1f5fe; color: #0277bd; padding: 4px 8px; border-radius: 12px; font-size: 12px;">
                        {goal['category']}
                    </span>
                </div>
                <div style="margin-bottom: 5px;">
                    <span style="font-weight: bold;">Progress: {goal['progress']}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# AI Chat Section
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("💬 Chat with AI Assistant", use_container_width=True):
        st.session_state.show_ai_chat = True

# AI Chat Popup
if st.session_state.show_ai_chat:
    with st.expander("🤖 AI Assistant", expanded=True):
        st.markdown("**Chat with your AI Assistant**")
        
        # Display latest chat message only
        if st.session_state.chat_messages:
            latest_message = st.session_state.chat_messages[-1]
            
            # AI response summary container (on top)
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                color: white;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            ">
                <h4 style="margin-bottom: 10px; color: white;">💡 Summary</h4>
                <p style="margin: 0; font-size: 16px; line-height: 1.5;">{latest_message['ai_summary']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # AI detailed response
            st.markdown("**AI Response:**")
            st.markdown(f"<div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #667eea; margin-bottom: 15px;'>{latest_message['ai_response']}</div>", unsafe_allow_html=True)
            
            # User message (bottom right aligned)
            st.markdown(f"""
            <div style="text-align: right; margin: 20px 0;">
                <div style="
                    display: inline-block;
                    background-color: #e3f2fd;
                    border-radius: 15px;
                    padding: 10px 15px;
                    margin-left: 20%;
                    border: 1px solid #bbdefb;
                    text-align: left;
                ">
                    <strong>You:</strong> {latest_message['user']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Input area
        user_input = st.text_area(
            "Type your message:", 
            placeholder="Ask me anything about your goals...", 
            key="ai_chat_input",
            value=st.session_state.ai_input
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Send Message"):
                if user_input.strip():
                    # Simulate AI response (replace with your AI integration)
                    ai_summary = "This is a sample summary of the AI's key insights and recommendations."
                    ai_response = "This is the detailed AI response that would come from your integrated AI system. It provides comprehensive guidance and actionable advice."
                    
                    # Replace chat history with new message (only keep latest)
                    st.session_state.chat_messages = [{
                        'user': user_input,
                        'ai_summary': ai_summary,
                        'ai_response': ai_response
                    }]
                    
                    # Clear input
                    st.session_state.ai_input = ""
                    st.rerun()
                
        with col2:
            if st.button("Close Chat"):
                st.session_state.show_ai_chat = False
                st.rerun()

# Generate Future Responses Section
st.markdown("---")

# Center the button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔮 Generate Future Paths", use_container_width=True):
        st.session_state.show_future_paths = True

# Future Paths Popup
if st.session_state.show_future_paths:
    with st.expander("🛤️ Explore Your Future Paths", expanded=True):
        st.markdown("**Choose your next direction:**")
        
        # Three different paths
        paths = [
            {
                "title": "🚀 Accelerated Growth Path",
                "description": "Focus on rapid skill development and aggressive goal pursuit",
                "benefits": ["Faster results", "High impact actions", "Intensive learning"],
                "timeframe": "3-6 months"
            },
            {
                "title": "⚖️ Balanced Development Path",
                "description": "Maintain steady progress across all life areas",
                "benefits": ["Sustainable progress", "Work-life balance", "Holistic growth"],
                "timeframe": "6-12 months"
            },
            {
                "title": "🔄 Pivot & Explore Path",
                "description": "Experiment with new directions and reassess current goals",
                "benefits": ["New opportunities", "Reduced risk", "Discovery focus"],
                "timeframe": "1-3 months exploration"
            }
        ]
        
        cols = st.columns(3)
        
        for i, path in enumerate(paths):
            with cols[i]:
                st.markdown(f"""
                <div style="
                    border: 2px solid #4CAF50;
                    border-radius: 15px;
                    padding: 20px;
                    margin: 10px 0;
                    background-color: #f8fff8;
                    text-align: center;
                ">
                    <h4 style="color: #2E7D32; margin-bottom: 15px;">{path['title']}</h4>
                    <p style="color: #555; margin-bottom: 15px; font-size: 14px;">{path['description']}</p>
                    <div style="margin-bottom: 15px;">
                        <strong style="color: #2E7D32;">Benefits:</strong>
                        <ul style="list-style: none; padding: 0; margin: 10px 0;">
                """, unsafe_allow_html=True)
                
                for benefit in path['benefits']:
                    st.markdown(f"<li style='color: #666; font-size: 13px;'>• {benefit}</li>", unsafe_allow_html=True)
                
                st.markdown(f"""
                        </ul>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <strong style="color: #2E7D32;">Timeframe:</strong>
                        <p style="color: #666; font-size: 13px; margin: 5px 0;">{path['timeframe']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Choose Path {i+1}", key=f"path_{i}"):
                    st.success(f"You've selected the {path['title']}!")
                    st.balloons()
        
        st.markdown("---")
        if st.button("Close Paths", use_container_width=True):
            st.session_state.show_future_paths = False
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 14px;'>"
    "Your journey to success starts with clear goals and smart decisions 🎯"
    "</div>", 
    unsafe_allow_html=True
)