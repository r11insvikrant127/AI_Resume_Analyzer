# chat_view.py

import streamlit as st
from datetime import timezone
from zoneinfo import ZoneInfo

from db_operations import (
    create_chat_session,
    append_chat_message,
    list_chat_messages,
    list_user_chat_sessions,
    delete_chat_session,
)
from interview_chatbot import (
    start_simulation,
    next_simulation_turn,
    answer_question,
)

def to_ist(dt):
    """Convert a stored UTC timestamp to Indian Standard Time."""
    if dt is None:
        return ""

    # MySQL/SQLAlchemy currently stores UTC as a naive datetime.
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(ZoneInfo("Asia/Kolkata"))

def _history_as_messages(rows):
    return [{"role": r.role, "content": r.content} for r in rows]


def render_chat(client, model, analysis, mode):
    """
    Render a chat UI for the given analysis + mode.

    mode: "simulation" or "qa"
    """

    user_id = st.session_state["user_id"]

    resume_text = analysis.get("resume_text", "")
    jd_text = analysis.get("job_description", "") or \
              st.session_state.get("job_description", "")
    question_bank = analysis.get("interview_questions", [])

    key = f"chat_session_{mode}_{analysis.get('resume_name')}"

    # --------------------------------------------------------
    # Existing sessions dropdown
    # --------------------------------------------------------

    prior = [
        s for s in list_user_chat_sessions(user_id)
        if s.mode == mode and s.resume_name == analysis.get("resume_name")
    ]

    if prior:
        with st.expander("📂 Load a Previous Session"):
            for s in prior:
                c1, c2 = st.columns([4, 1])
                with c1:
                    if st.button(
                        f"#{s.id} — {s.title} "
                        f"({to_ist(s.created_at).strftime('%Y-%m-%d %H:%M')})",
                        key=f"load_chat_{s.id}",
                    ):
                        st.session_state[key] = s.id
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_chat_{s.id}"):
                        delete_chat_session(s.id, user_id)
                        if st.session_state.get(key) == s.id:
                            st.session_state.pop(key, None)
                        st.rerun()

    # --------------------------------------------------------
    # Start new session if none loaded
    # --------------------------------------------------------

    if key not in st.session_state:

        st.info("No active session. Start a new one below.")

        if st.button("Start New Chat", type="primary"):

            session_id = create_chat_session(
                user_id=user_id,
                mode=mode,
                resume_name=analysis.get("resume_name"),
                title=f"{mode} · {analysis.get('resume_name', 'resume')}",
            )

            st.session_state[key] = session_id

            # Prime simulation with the opening question
            if mode == "simulation":
                opener = start_simulation(
                    client, model, resume_text, jd_text, question_bank
                )
                append_chat_message(session_id, "assistant", opener)

            st.rerun()

        return

    session_id = st.session_state[key]

    # --------------------------------------------------------
    # Render message history
    # --------------------------------------------------------

    msgs = list_chat_messages(session_id)

    for m in msgs:
        with st.chat_message(m.role):
            st.write(m.content)

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    user_input = st.chat_input(
        "Your answer..." if mode == "simulation" else "Your question..."
    )

    if user_input:

        # Show the user's message immediately
        with st.chat_message("user"):
            st.write(user_input)

        append_chat_message(session_id, "user", user_input)

        # Build history for the LLM (excluding current turn)
        history = _history_as_messages(msgs)

        with st.spinner("Thinking..."):

            if mode == "simulation":
                reply = next_simulation_turn(
                    client, model, resume_text, jd_text,
                    history, user_input,
                )
            else:
                reply = answer_question(
                    client, model, resume_text, jd_text,
                    history, user_input,
                )

        append_chat_message(session_id, "assistant", reply)

        with st.chat_message("assistant"):
            st.write(reply)

        st.rerun()

    # --------------------------------------------------------
    # End session
    # --------------------------------------------------------

    if st.button("End Chat", key=f"end_{session_id}"):
        st.session_state.pop(key, None)
        st.rerun()