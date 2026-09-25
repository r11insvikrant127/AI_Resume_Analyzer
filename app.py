#app.py

import os
import hashlib

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from analysis_pipeline import analyze_single_resume
from comparison_view import render_comparison
from admin_dashboard import render_admin_dashboard
from auth_views import require_login, render_logout_button
from report_view import render_single_report
from llm_analysis import analyze_resume

from keyword_analyzer import extract_keywords_from_jd


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

from db import init_db
init_db()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    st.error(
        "GROQ_API_KEY is missing. "
        "Please add it to your .env file."
    )
    st.stop()

client = Groq(api_key=API_KEY)
MODEL = "openai/gpt-oss-120b"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }

    .formula {
        font-family: monospace;
        background: #f6f6f6;
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid #e2e2e2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# AUTH GATE
# ============================================================

if not require_login():
    st.stop()

render_logout_button()


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">AI Resume Analyzer & Job Matcher</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Analyze your resume against a job description '
    'using Generative AI.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# CACHED JD SKILL EXTRACTION
# ============================================================

def get_jd_keywords(job_description):
    """
    Cache JD requirement extraction for the current session.
    """

    cache = st.session_state.setdefault("jd_keyword_cache", {})
    key = job_description.strip()

    if key in cache:
        return cache[key]

    requirement_data = extract_keywords_from_jd(
        client, MODEL, job_description
    )

    cache[key] = requirement_data
    return requirement_data


# ============================================================
# SIDEBAR + NAVIGATION
# ============================================================

page = "Analyzer"

with st.sidebar:

    st.header("Project Information")

    st.write(
        """
        This application uses Generative AI for semantic
        job-description analysis, resume matching, and
        qualitative resume analysis.

        Python performs the numerical ATS calculations.
        """
    )

    st.divider()

    st.subheader("Technology")
    st.write(
        """
        Python

        Streamlit

        Groq

        LLM

        PDF & DOCX Processing

        MySQL Storage

        Prompt Engineering
        """
    )

    st.divider()

    st.subheader("Analysis")
    st.write(
        """
        ATS Score

        ATS Keyword Analysis

        Requirement Matching

        Technical Skill Match

        Skill Gaps

        Candidate Ranking

        Multi-Resume Comparison

        Strengths / Weaknesses

        Resume Improvements

        Interview Questions

        Resume Rewriting

        Job Recommendations

        PDF Report Export
        """
    )

    if st.session_state.get("is_admin"):
        st.divider()
        page = st.radio(
            "Navigate",
            ["Analyzer", "Admin Dashboard"],
            key="nav_radio",
        )


if page == "Admin Dashboard":
    render_admin_dashboard()
    st.stop()


# ============================================================
# MAIN INPUTS
# ============================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Resume")
    uploaded_files = st.file_uploader(
        "Upload Resume(s) — PDF or DOCX",
        type=["pdf", "docx"],
        accept_multiple_files=True,
    )

with col2:
    st.subheader("2. Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=250,
        placeholder="Paste the complete job description...",
    )


# ============================================================
# ANALYZE BUTTON
# ============================================================

st.divider()

analyze_button = st.button(
    "Analyze Resume",
    type="primary",
    use_container_width=True,
)


# ============================================================
# PROCESS
# ============================================================

if analyze_button:

    if not uploaded_files:
        st.warning("Please upload at least one resume (PDF or DOCX).")
        st.stop()

    if not job_description.strip():
        st.warning("Please enter a job description.")
        st.stop()

    with st.spinner("Extracting job requirements..."):
        try:
            requirement_data = get_jd_keywords(job_description)
        except Exception as e:
            st.error(f"Failed to analyze job description: {e}")
            st.stop()

    results = []
    errors = []

    progress = st.progress(0.0)

    for index, uploaded_file in enumerate(uploaded_files):

        try:
            with st.spinner(f"Analyzing {uploaded_file.name}..."):

                result = analyze_single_resume(
                    uploaded_file=uploaded_file,
                    job_description=job_description,
                    requirement_data=requirement_data,
                    analyze_resume_llm=lambda text, jd: analyze_resume(
                        client, MODEL, text, jd
                    ),
                    client=client,
                    model=MODEL,
                )

                try:
                    from db_operations import save_resume, save_analysis

                    resume_id = save_resume(
                        user_id=st.session_state["user_id"],
                        filename=uploaded_file.name,
                        file_hash=hashlib.sha256(
                            result["resume_text"].encode("utf-8")
                        ).hexdigest(),
                        raw_text=result["resume_text"],
                    )

                    save_analysis(
                        user_id=st.session_state["user_id"],
                        resume_id=resume_id,
                        resume_name=result["resume_name"],
                        jd_text=job_description,
                        result=result,
                    )
                except Exception as db_err:
                    st.warning(
                        f"{uploaded_file.name}: saved locally but "
                        f"could not persist to DB ({db_err})."
                    )

                # Attach JD text so report_view can render rewrite
                result["job_description"] = job_description

                results.append(result)

        except Exception as e:
            errors.append((uploaded_file.name, str(e)))

        progress.progress((index + 1) / len(uploaded_files))

    progress.empty()

    for name, message in errors:
        st.warning(f"{name}: {message}")

    if not results:
        st.error("No resumes could be analyzed.")
        st.stop()

    st.session_state["results"] = results
    st.session_state["job_description"] = job_description

    # Clear per-resume derived state
    for key in list(st.session_state.keys()):
        if (
            key.startswith("rewrite_")
            or key.startswith("tips_")
            or key == "recommendations"
        ):
            st.session_state.pop(key, None)

    if len(results) == 1:
        st.session_state["analysis"] = results[0]
        st.session_state["resume_text"] = results[0]["resume_text"]
    else:
        st.session_state.pop("analysis", None)
        st.session_state.pop("resume_text", None)

    st.success(f"Analyzed {len(results)} resume(s).")


# ============================================================
# SINGLE-RESUME REPORT
# ============================================================

if "analysis" in st.session_state:

    st.divider()
    st.header("Resume Analysis Report")

    render_single_report(
        st.session_state["analysis"],
        client=client,
        model=MODEL,
        show_pdf_download=True,
        show_extras=True,
    )


# ============================================================
# MULTI-RESUME COMPARISON VIEW
# ============================================================

if (
    "results" in st.session_state
    and len(st.session_state["results"]) > 1
):

    st.divider()

    render_comparison(
        st.session_state["results"],
        client=client,
        model=MODEL,
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption("AI Resume Analyzer | Python + Streamlit + Groq + MySQL")