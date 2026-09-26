import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st

from page_utils import page_setup
from chat_view import render_chat
from db_operations import list_user_analyses_with_pagination
from styles import hero, section

client, MODEL = page_setup("Interview Chat", "🎤")

hero(
    "Interview Chatbot",
    "Mock interviews and Q&A grounded in your resume and JD.",
    badges=["Simulation", "Q&A", "History Saved"],
)

user_id = st.session_state["user_id"]

analyses = list_user_analyses_with_pagination(user_id, limit=50)

if not analyses:
    st.info("Run an analysis first, then come back to practice.")
    st.stop()

analysis_map = {a.id: a for a in analyses}

section("🎯", "Choose a Session")

chosen_id = st.selectbox(
    "Pick an analysis",
    options=list(analysis_map.keys()),
    format_func=lambda i: (
        f"#{i} — {analysis_map[i].resume_name} "
        f"({analysis_map[i].created_at.strftime('%Y-%m-%d')})"
    ),
)

chosen = analysis_map[chosen_id]

mode = st.radio(
    "Mode",
    ["simulation", "qa"],
    format_func=lambda m: (
        "🎭 Mock Interview" if m == "simulation" else "💬 Q&A"
    ),
    horizontal=True,
)

render_chat(client, MODEL, chosen.result_json, mode)