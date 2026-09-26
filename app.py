#app.py

import os
import hashlib

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from analysis_pipeline import analyze_single_resume
from comparison_view import render_comparison
from auth_views import require_login, render_logout_button
from report_view import render_single_report
from llm_analysis import analyze_resume
from keyword_analyzer import extract_keywords_from_jd

from styles import (
    inject_theme,
    hero,
    section,
    sidebar_brand,
    sidebar_section,
    sidebar_item,
    footer,
)


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

from db import init_db_cached
init_db_cached()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    st.error("GROQ_API_KEY is missing. Add it to your .env file.")
    st.stop()

@st.cache_resource(show_spinner=False)
def _make_client(key):
    return Groq(api_key=key)

client = _make_client(API_KEY)
MODEL = "openai/gpt-oss-120b"


# ============================================================
# PAGE CONFIG + THEME
# ============================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
)
from styles import loading_bar
bar = loading_bar()
# Inject theme BEFORE the auth gate so the login page is styled
inject_theme()


# ============================================================
# AUTH GATE
# ============================================================

if not require_login():
    st.stop()

render_logout_button()


# ============================================================
# HERO
# ============================================================
bar.empty()
hero(
    title="AI Resume Analyzer & Job Matcher",
    subtitle=(
        "Compare your resume against any job description, "
        "find skill gaps, and get AI-generated feedback."
    ),
    badges=[
        "ATS Scoring",
        "Multi-Resume Ranking",
        "Interview Chatbot",
        "Knowledge Base",
    ],
)


# ============================================================
# CACHED JD SKILL EXTRACTION
# ============================================================

def get_jd_keywords(job_description):
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
# SIDEBAR
# ============================================================

with st.sidebar:

    sidebar_brand()

    sidebar_section("Technology")
    for item in [
        "🐍 Python",
        "⚡ Streamlit",
        "🤖 Groq · LLM",
        "📄 PDF & DOCX",
        "🗄️ MySQL",
        "🔎 FAISS Vector Search",
    ]:
        sidebar_item(item)

    sidebar_section("Capabilities")
    for item in [
        "📊 ATS Score",
        "🔑 Keyword Analysis",
        "🎯 Requirement Matching",
        "🧠 Skill Gap Analysis",
        "🏆 Candidate Ranking",
        "📚 Resume History",
        "🎤 Interview Chatbot",
        "📖 Knowledge Base",
        "✍️ Resume Rewriting",
        "💼 Job Recommendations",
        "⬇️ PDF Export",
    ]:
        sidebar_item(item)


# ============================================================
# MAIN INPUTS
# ============================================================

section("📤", "Analyze a Resume", "Upload one or more resumes and paste the JD")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    with st.container(border=True):
        st.markdown("**1 · Upload Resume(s)**")
        st.caption("PDF or DOCX · multiple files supported")
        uploaded_files = st.file_uploader(
            "Upload Resume(s)",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

with col2:
    with st.container(border=True):
        st.markdown("**2 · Job Description**")
        st.caption("Paste the full JD for best matching accuracy")
        job_description = st.text_area(
            "Job Description",
            height=210,
            placeholder="Paste the complete job description here...",
            label_visibility="collapsed",
        )


st.write("")

analyze_button = st.button(
    "🚀 Analyze Resume",
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

    st.success(f"✅ Analyzed {len(results)} resume(s).")


# ============================================================
# SINGLE-RESUME REPORT
# ============================================================

if "analysis" in st.session_state:

    section("📊", "Resume Analysis Report")

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

    section("🏆", "Resume Comparison")

    render_comparison(
        st.session_state["results"],
        client=client,
        model=MODEL,
    )


# ============================================================
# FOOTER
# ============================================================

footer()