# admin_dashboard.py

import streamlit as st
from datetime import timezone
from zoneinfo import ZoneInfo

from db_operations import list_all_users, list_all_analyses


IST = ZoneInfo("Asia/Kolkata")


def to_ist(dt):
    """Convert a stored UTC timestamp to Indian Standard Time."""
    if dt is None:
        return ""

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(IST)


def render_admin_dashboard():
    if not st.session_state.get("is_admin"):
        st.error("Admin access only.")
        return

    st.header("🛠️ Admin Dashboard")

    users = list_all_users()
    analyses = list_all_analyses()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Total Users", len(users))

    with c2:
        st.metric("Total Analyses", len(analyses))

    with c3:
        avg_ats = (
            round(sum(a.ats_score for a in analyses) / len(analyses), 1)
            if analyses else 0
        )
        st.metric("Average ATS Score", f"{avg_ats}%")

    st.divider()

    st.subheader("Users")

    user_rows = [
        {
            "ID": u.id,
            "Email": u.email,
            "Name": u.full_name or "—",
            "Admin": "Yes" if u.is_admin else "No",
            "Joined": to_ist(u.created_at).strftime("%Y-%m-%d"),
        }
        for u in users
    ]

    st.dataframe(user_rows, use_container_width=True)

    st.divider()

    st.subheader("Recent Analyses")

    analysis_rows = [
        {
            "ID": a.id,
            "User ID": a.user_id,
            "Resume": a.resume_name,
            "ATS": f"{a.ats_score}%",
            "Required": f"{a.required_match_percentage}%",
            "Technical": f"{a.technical_skill_percentage}%",
            "Date": to_ist(a.created_at).strftime("%Y-%m-%d %H:%M"),
        }
        for a in analyses
    ]

    st.dataframe(analysis_rows, use_container_width=True)

    st.divider()

    st.subheader("View a Result")

    if analyses:
        selected = st.selectbox(
            "Pick an analysis ID",
            [a.id for a in analyses],
        )
        row = next((a for a in analyses if a.id == selected), None)
        if row:
            st.json(row.result_json)