import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st

from page_utils import page_setup
from chat_view import render_chat
from db_operations import list_user_analyses_with_pagination

client, MODEL = page_setup("Interview Chat", "🎤")

st.header("🎤 Interview Chatbot")
st.caption(
    "Mock interviews and Q&A, grounded in a specific "
    "resume + JD you've already analyzed."
)

user_id = st.session_state["user_id"]

analyses = list_user_analyses_with_pagination(user_id, limit=50)

if not analyses:
    st.info("Run an analysis first, then come back.")
    st.stop()

analysis_map = {a.id: a for a in analyses}

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
        "Mock Interview" if m == "simulation" else "Q&A"
    ),
    horizontal=True,
)

render_chat(client, MODEL, chosen.result_json, mode)