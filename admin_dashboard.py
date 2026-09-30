import copy
import textwrap
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


def _metric_card(title, value, icon):
    with st.container(border=True):
        st.markdown(
            textwrap.dedent(
                f"""
                <div style="
                    display:flex;
                    align-items:center;
                    gap:12px;
                    margin-bottom:4px;
                ">
                    <span style="font-size:24px;">{icon}</span>
                    <span style="
                        font-size:13px;
                        color:#64748b;
                        font-weight:600;
                    ">
                        {title}
                    </span>
                </div>

                <div style="
                    font-size:30px;
                    font-weight:700;
                    color:#1e293b;
                ">
                    {value}
                </div>
                """
            ),
            unsafe_allow_html=True,
        )


def _section_title(icon, title, description=None):
    description_html = (
        f"""
        <div style="
            margin-top:4px;
            color:#64748b;
            font-size:13px;
        ">
            {description}
        </div>
        """
        if description
        else ""
    )

    st.markdown(
        textwrap.dedent(
            f"""
            <div style="
                margin-top:8px;
                margin-bottom:14px;
            ">
                <div style="
                    display:flex;
                    align-items:center;
                    gap:10px;
                    font-size:22px;
                    font-weight:700;
                    color:#1e293b;
                ">
                    <span>{icon}</span>
                    <span>{title}</span>
                </div>

                {description_html}
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _render_list(items, empty_message="None"):
    if not items:
        st.caption(empty_message)
        return

    for item in items:
        st.markdown(
            textwrap.dedent(
                f"""
                <div style="
                    padding:9px 12px;
                    margin-bottom:7px;
                    background:#f8fafc;
                    border:1px solid #e2e8f0;
                    border-radius:8px;
                    color:#334155;
                    font-size:14px;
                ">
                    {item}
                </div>
                """
            ),
            unsafe_allow_html=True,
        )


def _render_analysis_result(row):
    result = row.result_json or {}

    # --------------------------------------------------------
    # ANALYSIS HEADER
    # --------------------------------------------------------

    st.markdown(
        textwrap.dedent(
            f"""
            <div style="
                padding:18px 20px;
                border:1px solid #e2e8f0;
                border-radius:12px;
                background:#f8fafc;
                margin-bottom:18px;
            ">
                <div style="
                    font-size:13px;
                    color:#64748b;
                    margin-bottom:5px;
                ">
                    RESUME
                </div>

                <div style="
                    font-size:20px;
                    font-weight:700;
                    color:#1e293b;
                ">
                    {row.resume_name}
                </div>

                <div style="
                    font-size:13px;
                    color:#64748b;
                    margin-top:5px;
                ">
                    Analysis ID: {row.id}
                    &nbsp; · &nbsp;
                    User ID: {row.user_id}
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SCORE CARDS
    # --------------------------------------------------------

    score_col1, score_col2, score_col3, score_col4 = st.columns(4)

    with score_col1:
        _metric_card(
            "ATS Score",
            f"{row.ats_score}%",
            "🎯",
        )

    with score_col2:
        _metric_card(
            "Required Match",
            f"{row.required_match_percentage}%",
            "🔑",
        )

    with score_col3:
        _metric_card(
            "Technical Match",
            f"{row.technical_skill_percentage}%",
            "💻",
        )

    with score_col4:
        _metric_card(
            "Good-to-have",
            f"{row.good_to_have_match_percentage}%",
            "⭐",
        )

    st.write("")

    # --------------------------------------------------------
    # CANDIDATE SUMMARY
    # --------------------------------------------------------

    summary = result.get("candidate_summary")

    if summary:
        _section_title(
            "👤",
            "Candidate Summary",
        )

        with st.container(border=True):
            st.write(summary)

    # --------------------------------------------------------
    # MATCH ANALYSIS
    # --------------------------------------------------------

    experience_match = result.get("experience_match")
    education_match = result.get("education_match")
    project_match = result.get("project_match")

    if any(
        [
            experience_match,
            education_match,
            project_match,
        ]
    ):

        _section_title(
            "📊",
            "Match Analysis",
        )

        match_col1, match_col2 = st.columns(2)

        with match_col1:

            if experience_match:
                with st.container(border=True):
                    st.markdown("**Experience Match**")
                    st.write(experience_match)

            if education_match:
                with st.container(border=True):
                    st.markdown("**Education Match**")
                    st.write(education_match)

        with match_col2:

            if project_match:
                with st.container(border=True):
                    st.markdown("**Project Match**")
                    st.write(project_match)

    # --------------------------------------------------------
    # STRENGTHS / WEAKNESSES
    # --------------------------------------------------------

    strengths = result.get("strengths", [])
    weaknesses = result.get("weaknesses", [])

    if strengths or weaknesses:

        _section_title(
            "⚖️",
            "Strengths & Weaknesses",
        )

        strength_col, weakness_col = st.columns(2)

        with strength_col:
            with st.container(border=True):
                st.markdown("### ✅ Strengths")
                _render_list(strengths)

        with weakness_col:
            with st.container(border=True):
                st.markdown("### ⚠️ Weaknesses")
                _render_list(weaknesses)

    # --------------------------------------------------------
    # SKILL GAP
    # --------------------------------------------------------

    skill_gap = result.get("skill_gap", {})

    if skill_gap:

        _section_title(
            "🧠",
            "Skill Gap Analysis",
        )

        gap_col1, gap_col2, gap_col3 = st.columns(3)

        with gap_col1:
            with st.container(border=True):
                st.markdown("**Matched Required**")

                _render_list(
                    skill_gap.get(
                        "matched_required",
                        [],
                    ),
                    "No matched required skills.",
                )

        with gap_col2:
            with st.container(border=True):
                st.markdown("**High Priority Gaps**")

                _render_list(
                    skill_gap.get(
                        "high_priority_gaps",
                        [],
                    ),
                    "No high-priority gaps.",
                )

        with gap_col3:
            with st.container(border=True):
                st.markdown("**Good-to-have Gaps**")

                _render_list(
                    skill_gap.get(
                        "good_to_have_gaps",
                        [],
                    ),
                    "No good-to-have gaps.",
                )

        severity = skill_gap.get("overall_severity")

        if severity:
            st.caption(
                f"Overall skill-gap severity: "
                f"**{severity.title()}**"
            )

    # --------------------------------------------------------
    # RESUME IMPROVEMENTS
    # --------------------------------------------------------

    improvements = result.get(
        "resume_improvements",
        [],
    )

    if improvements:

        _section_title(
            "✍️",
            "Resume Improvements",
        )

        with st.container(border=True):
            _render_list(improvements)

    # --------------------------------------------------------
    # INTERVIEW QUESTIONS
    # --------------------------------------------------------

    interview_questions = result.get(
        "interview_questions",
        [],
    )

    if interview_questions:

        _section_title(
            "🎤",
            "Generated Interview Questions",
        )

        with st.container(border=True):

            for index, question in enumerate(
                interview_questions,
                start=1,
            ):
                st.markdown(
                    f"**{index}.** {question}"
                )

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    required_skills = result.get(
        "required_skills",
        [],
    )

    matched_skills = result.get(
        "matched_skills",
        [],
    )

    missing_skills = result.get(
        "missing_skills",
        [],
    )

    if (
        required_skills
        or matched_skills
        or missing_skills
    ):

        _section_title(
            "🧩",
            "Skill Matching",
        )

        skill_col1, skill_col2 = st.columns(2)

        with skill_col1:

            with st.container(border=True):
                st.markdown("**Matched Skills**")

                _render_list(
                    matched_skills,
                    "No matched skills.",
                )

        with skill_col2:

            with st.container(border=True):
                st.markdown("**Missing Skills**")

                _render_list(
                    missing_skills,
                    "No missing skills.",
                )

    # --------------------------------------------------------
    # KEYWORD ANALYSIS
    # --------------------------------------------------------

    keyword_analysis = result.get(
        "ats_keyword_analysis",
        {},
    )

    if keyword_analysis:

        _section_title(
            "🔎",
            "ATS Keyword Analysis",
        )

        keyword_rows = keyword_analysis.get(
            "keyword_rows",
            [],
        )

        if keyword_rows:

            rows = []

            for item in keyword_rows:
                rows.append(
                    {
                        "Keyword": item.get(
                            "keyword",
                            "",
                        ),
                        "Tier": item.get(
                            "tier",
                            "",
                        ),
                        "Count": item.get(
                            "count",
                            0,
                        ),
                        "In Skills Section": (
                            "Yes"
                            if item.get(
                                "in_skills_section"
                            )
                            else "No"
                        ),
                    }
                )

            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )

    # --------------------------------------------------------
    # FULL STORED RESULT
    # --------------------------------------------------------

    with st.expander(
        "🔧 View full stored analysis JSON"
    ):

        # Do not dump the entire resume text
        # into the main JSON viewer.
        display_result = copy.deepcopy(
            result
        )

        display_result.pop(
            "resume_text",
            None,
        )

        st.json(display_result)

    # --------------------------------------------------------
    # RAW RESUME TEXT
    # --------------------------------------------------------

    resume_text = result.get(
        "resume_text"
    )

    if resume_text:

        with st.expander(
            "📄 View extracted resume text"
        ):
            st.text(resume_text)


def render_admin_dashboard():

    if not st.session_state.get(
        "is_admin"
    ):
        st.error("Admin access only.")
        return

    users = list_all_users()
    analyses = list_all_analyses()

    # ========================================================
    # OVERVIEW
    # ========================================================

    _section_title(
        "📈",
        "Platform Overview",
        "Monitor users and resume-analysis activity.",
    )

    avg_ats = (
        round(
            sum(
                a.ats_score
                for a in analyses
            )
            / len(analyses),
            1,
        )
        if analyses
        else 0
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        _metric_card(
            "Total Users",
            len(users),
            "👥",
        )

    with c2:
        _metric_card(
            "Total Analyses",
            len(analyses),
            "📄",
        )

    with c3:
        _metric_card(
            "Average ATS Score",
            f"{avg_ats}%",
            "🎯",
        )

    st.write("")

    # ========================================================
    # USERS
    # ========================================================

    _section_title(
        "👥",
        "Users",
        "Registered accounts and administrator status.",
    )

    if users:

        user_rows = [
            {
                "ID": u.id,
                "Email": u.email,
                "Name": u.full_name or "—",
                "Admin": (
                    "Yes"
                    if u.is_admin
                    else "No"
                ),
                "Joined": to_ist(
                    u.created_at
                ).strftime(
                    "%d %b %Y"
                ),
            }
            for u in users
        ]

        with st.container(
            border=True
        ):
            st.dataframe(
                user_rows,
                use_container_width=True,
                hide_index=True,
            )

    else:

        with st.container(
            border=True
        ):
            st.info(
                "No registered users yet."
            )

    st.write("")

    # ========================================================
    # RECENT ANALYSES
    # ========================================================

    _section_title(
        "📊",
        "Recent Analyses",
        "Latest resume analyses stored in the platform.",
    )

    if analyses:

        analysis_rows = [
            {
                "ID": a.id,
                "User": a.user_id,
                "Resume": a.resume_name,
                "ATS": f"{a.ats_score}%",
                "Required": (
                    f"{a.required_match_percentage}%"
                ),
                "Technical": (
                    f"{a.technical_skill_percentage}%"
                ),
                "Date": to_ist(
                    a.created_at
                ).strftime(
                    "%d %b %Y, %H:%M"
                ),
            }
            for a in analyses
        ]

        with st.container(
            border=True
        ):
            st.dataframe(
                analysis_rows,
                use_container_width=True,
                hide_index=True,
            )

    else:

        with st.container(
            border=True
        ):
            st.info(
                "No resume analyses have "
                "been recorded yet."
            )

    st.write("")

    # ========================================================
    # VIEW RESULT
    # ========================================================

    _section_title(
        "🔍",
        "View Analysis Result",
        "Select an analysis to inspect its detailed report.",
    )

    if analyses:

        analysis_options = {
            a.id: a
            for a in analyses
        }

        selected_id = st.selectbox(
            "Select an analysis",
            list(
                analysis_options.keys()
            ),
            format_func=lambda analysis_id: (
                f"Analysis #{analysis_id} — "
                f"{analysis_options[analysis_id].resume_name}"
            ),
        )

        selected = analysis_options[
            selected_id
        ]

        _render_analysis_result(
            selected
        )

    else:

        with st.container(
            border=True
        ):
            st.info(
                "Run a resume analysis first "
                "to view its result here."
            )