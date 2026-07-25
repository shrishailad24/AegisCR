import streamlit as st
import json
from openai import OpenAI

# Set up clean web page layout
st.set_page_config(page_title="AAROHA Human OS", page_icon="🧠", layout="wide")

import os

# 1. Initialize AI Client
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", "")) if hasattr(st, "secrets") else os.environ.get("GROQ_API_KEY", "")
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

# 2. Hardcoded User Genome (Your baseline profile)
USER_GENOME = {
    "name": "Shash",
    "financials": {
        "current_monthly_income": 85000,
        "target_savings_goal": 1000000 
    },
    "career": {
        "current_skills": ["Python", "SQL", "Data Analytics"],
        "long_term_target_role": "Senior Data Scientist",
        "preferences": {
            "prefers_remote": True
        }
    }
}

# --- WEB UI HEADER ---
st.title("🧠 AAROHA: Human Operating System")
st.markdown("---")

# Layout columns: Left side for inputs, Right side for AI output
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("📥 Job Scenario Input")
    
    # Interactive UI Widgets
    salary_input = st.slider("💰 Proposed Monthly Salary:", min_value=50000, max_value=300000, value=130000, step=5000)
    skills_input = st.text_input("🛠️ Required Job Skills:", "Excel, Tableau, SQL")
    remote_input = st.radio("🏡 Is this job remote?", ["Yes", "No"])
    
    submit_button = st.button("🚀 Run AAROHA Matrix Engine", type="primary")

with col2:
    st.header("🤖 Decision Brief Output")
    
    if submit_button:
        # Structure payload
        proposed_scenario = {
            "role": "New Job Candidate Offer",
            "salary": salary_input,
            "required_skills": [s.strip() for s in skills_input.split(",")],
            "is_remote": remote_input == "Yes"
        }
        
        # Build prompt profiles
        system_prompt = (
            "You are AAROHA, a sophisticated Human Operating System layer. "
            "Deliver a hyper-personalized, analytical advisory brief. "
            "Format your response cleanly using bold markdown and markdown headers."
        )
        
        user_prompt = f"""
        Analyze this trade-off for the user.
        User Genome: {json.dumps(USER_GENOME)}
        New Scenario: {json.dumps(proposed_scenario)}
        
        Provide a structured briefing:
        1. QUANTITATIVE ALIGNMENT
        2. STRATEGIC CAREER ALIGNMENT
        3. FINAL CORE DIRECTIVE (Accept, Decline, or Negotiate)
        """
        
        with st.spinner("Processing context matrices..."):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2
                )
                # Render results to web screen
                st.success("Analysis Complete!")
                st.markdown(completion.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")
    else:
        st.info("Adjust the parameters on the left and click 'Run AAROHA Matrix Engine' to stream intelligence analysis.")