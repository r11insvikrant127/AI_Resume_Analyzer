import os
import json
import re

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from groq import Groq

from keyword_analyzer import (
    extract_keywords_from_jd,
    calculate_keyword_match,
    match_deterministic_skills,
    split_technical_skills          # NEW
)

from ats_scorer import (
    calculate_skill_match,
    calculate_ats_score
)

from skill_gap_analyzer import (
    build_skill_gap_analysis
)


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

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
    layout="wide"
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
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">'
    'AI Resume Analyzer & Job Matcher'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analyze your resume against a job description '
    'using Generative AI.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# FUNCTIONS
# ============================================================

def extract_resume_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n".join(pages)
    except Exception as e:
        raise Exception(f"Unable to read PDF: {e}")


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def analyze_resume(resume_text, job_description):
    """
    LLM is used ONLY for qualitative narrative.
    No scoring, no skill classification.
    """

    prompt = f"""
You are an expert technical recruiter and ATS resume analyzer.

Analyze the candidate resume against the provided job description.

Your response MUST be valid JSON.

Return exactly this structure:

{{
    "candidate_summary": "",
    "strengths": [],
    "weaknesses": [],
    "experience_match": "",
    "education_match": "",
    "project_match": "",
    "resume_improvements": [],
    "interview_questions": []
}}

Rules:

1. Do not invent candidate experience.
2. Base the analysis only on the provided resume and job description.
3. interview_questions should contain 10 relevant questions.
4. Keep the answer concise but useful.
5. Return JSON only.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional ATS resume analyzer. "
                    "Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content
    return parse_json_response(content)


def parse_json_response(content):
    content = content.strip()
    content = re.sub(r"^```json\s*", "", content, flags=re.IGNORECASE)
    content = re.sub(r"^```\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            return json.loads(content[start:end + 1])
        raise ValueError(
            "The AI returned an invalid response. Please try again."
        )


def generate_resume_tips(resume_text):
    prompt = f"""
Review this resume as a professional technical recruiter.

Provide 8 practical recommendations to improve it.

Focus on:
- ATS compatibility
- Technical skills
- Project descriptions
- Achievement statements
- Keywords
- Formatting
- Quantifiable results
- Professional summary

Resume:

{resume_text}

Return only a numbered list.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert resume coach."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


# ============================================================
# CACHED JD KEYWORD EXTRACTION   # NEW
# ============================================================

def get_jd_keywords(job_description):
    """
    Cache JD keyword extraction per unique JD within the
    Streamlit session. Avoids re-calling Groq on repeated
    "Analyze Resume" presses for the same JD.
    """

    cache = st.session_state.setdefault("jd_keyword_cache", {})
    key = job_description.strip()

    if key in cache:
        return cache[key]

    keyword_data = extract_keywords_from_jd(
        client, MODEL, job_description
    )

    cache[key] = keyword_data
    return keyword_data


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Project Information")

    st.write(
        """
        This application uses Generative AI for qualitative
        analysis and deterministic Python for ATS scoring
        and skill matching.
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

        PDF Processing

        Prompt Engineering
        """
    )

    st.divider()

    st.subheader("Analysis")

    st.write(
        """
        ATS Score

        Keyword Analysis

        Technical Skill Match

        Skill Gaps

        Strengths / Weaknesses

        Resume Improvements

        Interview Questions
        """
    )


# ============================================================
# MAIN INPUTS
# ============================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"]
    )

with col2:
    st.subheader("2. Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=250,
        placeholder="Paste the complete job description..."
    )


# ============================================================
# ANALYZE BUTTON
# ============================================================

st.divider()

analyze_button = st.button(
    "Analyze Resume",
    type="primary",
    use_container_width=True
)


# ============================================================
# PROCESS
# ============================================================

if analyze_button:

    if uploaded_file is None:
        st.warning("Please upload a resume PDF.")
        st.stop()

    if not job_description.strip():
        st.warning("Please enter a job description.")
        st.stop()

    with st.spinner("Reading and analyzing resume..."):

        try:
            # --------------------------------------------------
            # Resume text
            # --------------------------------------------------

            resume_text = extract_resume_text(uploaded_file)
            resume_text = clean_text(resume_text)

            if len(resume_text) < 100:
                st.error(
                    "Very little text was extracted from the PDF. "
                    "Please upload a text-based PDF."
                )
                st.stop()

            # --------------------------------------------------
            # LLM narrative
            # --------------------------------------------------

            result = analyze_resume(resume_text, job_description)

            # --------------------------------------------------
            # JD keywords (cached)
            # --------------------------------------------------

            keyword_data = get_jd_keywords(job_description)

            required_keywords = keyword_data.get(
                "required_keywords", []
            )
            good_to_have_keywords = keyword_data.get(
                "good_to_have_keywords", []
            )

            # --------------------------------------------------
            # Required keyword match (all required keywords)
            # --------------------------------------------------

            keyword_analysis = calculate_keyword_match(
                required_keywords,
                good_to_have_keywords,
                resume_text
            )

            # --------------------------------------------------
            # Deterministic skill classification
            # --------------------------------------------------

            det = match_deterministic_skills(
                required_skills=required_keywords,
                good_to_have_skills=good_to_have_keywords,
                resume_text=resume_text
            )

            # --------------------------------------------------
            # Split required skills into technical vs non-technical
            # -> used for the Technical Skill Match component
            # --------------------------------------------------

            required_technical, required_non_technical = (
                split_technical_skills(
                    det["matched_required"]
                    + det["partial_required"]
                    + det["missing_required"]
                )
            )

            def subset(skills, pool):
                return [s for s in skills if s in pool]

            tech_matched = subset(
                det["matched_required"], required_technical
            )
            tech_partial = subset(
                det["partial_required"], required_technical
            )
            tech_missing = subset(
                det["missing_required"], required_technical
            )

            # --------------------------------------------------
            # Technical Skill Match %
            # --------------------------------------------------

            technical_skill_percentage = calculate_skill_match(
                tech_matched,
                tech_missing,
                tech_partial
            )

            # --------------------------------------------------
            # Skill-gap analysis (deterministic)
            # --------------------------------------------------

            skill_gap = build_skill_gap_analysis(
                matched_required=det["matched_required"],
                partial_required=det["partial_required"],
                missing_required=det["missing_required"],
                matched_good_to_have=det["matched_good_to_have"],
                partial_good_to_have=det["partial_good_to_have"],
                missing_good_to_have=det["missing_good_to_have"]
            )

            # --------------------------------------------------
            # Final ATS score
            # --------------------------------------------------

            ats_score = calculate_ats_score(
                keyword_analysis["required_percentage"],
                technical_skill_percentage,
                keyword_analysis["good_to_have_percentage"]
            )

            # --------------------------------------------------
            # Store results
            # --------------------------------------------------

            result["required_keywords"] = required_keywords
            result["good_to_have_keywords"] = good_to_have_keywords

            result["matched_required_keywords"] = (
                keyword_analysis["matched_required"]
            )
            result["missing_required_keywords"] = (
                keyword_analysis["missing_required"]
            )
            result["matched_good_to_have_keywords"] = (
                keyword_analysis["matched_good_to_have"]
            )
            result["missing_good_to_have_keywords"] = (
                keyword_analysis["missing_good_to_have"]
            )

            result["required_keyword_percentage"] = (
                keyword_analysis["required_percentage"]
            )
            result["good_to_have_percentage"] = (
                keyword_analysis["good_to_have_percentage"]
            )
            result["keyword_match_percentage"] = (
                keyword_analysis["overall_percentage"]
            )

            # Technical-only skill lists (used by UI + scoring)
            result["technical_matched_skills"] = tech_matched
            result["technical_partial_skills"] = tech_partial
            result["technical_missing_skills"] = tech_missing
            result["technical_skill_percentage"] = (
                technical_skill_percentage
            )

            # Full required skill lists (for display)
            result["matched_skills"] = det["matched_required"]
            result["partial_match_skills"] = det["partial_required"]
            result["missing_skills"] = det["missing_required"]

            result["skill_match_percentage"] = technical_skill_percentage
            result["ats_score"] = ats_score
            result["skill_gap"] = skill_gap

            st.session_state["analysis"] = result
            st.session_state["resume_text"] = resume_text
            st.session_state["job_description"] = job_description

            st.success("Resume analysis completed successfully!")

        except Exception as e:
            st.error(f"Analysis failed: {e}")


# ============================================================
# DISPLAY RESULTS
# ============================================================

if "analysis" in st.session_state:

    result = st.session_state["analysis"]

    st.divider()
    st.header("Resume Analysis Report")

    # --------------------------------------------------------
    # Headline metrics
    # --------------------------------------------------------

    score = result.get("ats_score", 0)
    required_score = result.get("required_keyword_percentage", 0)
    tech_score = result.get("technical_skill_percentage", 0)
    good_to_have_score = result.get("good_to_have_percentage", 0)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("ATS Score", f"{score}%")

    with c2:
        st.metric(
            "Required Keyword Match",
            f"{required_score}%"
        )

    with c3:
        st.metric(
            "Technical Skill Match",
            f"{tech_score}%"
        )

    st.progress(min(max(score, 0), 100) / 100)

    # --------------------------------------------------------
    # Explicit score calculation  # NEW
    # --------------------------------------------------------

    st.subheader("How This ATS Score Was Calculated")

    req_contrib = round(required_score * 0.50, 2)
    tech_contrib = round(tech_score * 0.40, 2)
    good_contrib = round(good_to_have_score * 0.10, 2)

    st.markdown(
        f"""
<div class="formula">
Required Keyword Match : {required_score}% × 0.50 = {req_contrib}<br>
Technical Skill Match  : {tech_score}% × 0.40 = {tech_contrib}<br>
Good-to-Have Match     : {good_to_have_score}% × 0.10 = {good_contrib}<br>
<hr>
<b>Final ATS Score = {score}%</b>
</div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Keyword analysis
    # --------------------------------------------------------

    st.subheader("ATS Keyword Analysis")

    overall_keyword_score = result.get(
        "keyword_match_percentage", 0
    )

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric("Required Keyword Match", f"{required_score}%")

    with k2:
        st.metric("Good-to-Have Match", f"{good_to_have_score}%")

    with k3:
        st.metric("Overall Keyword Match", f"{overall_keyword_score}%")

    st.markdown("### Required Keywords")

    rc1, rc2 = st.columns(2)

    with rc1:
        st.markdown("#### Matched")
        matched_required = result.get(
            "matched_required_keywords", []
        )
        if matched_required:
            for keyword in matched_required:
                st.write(f"✓ {keyword}")
        else:
            st.write("No required keywords matched.")

    with rc2:
        st.markdown("#### Missing")
        missing_required = result.get(
            "missing_required_keywords", []
        )
        if missing_required:
            for keyword in missing_required:
                st.write(f"• {keyword}")
        else:
            st.write("No required keywords are missing.")

    st.markdown("### Good-to-Have Keywords")

    gc1, gc2 = st.columns(2)

    with gc1:
        st.markdown("#### Matched")
        matched_good = result.get(
            "matched_good_to_have_keywords", []
        )
        if matched_good:
            for keyword in matched_good:
                st.write(f"✓ {keyword}")
        else:
            st.write("No good-to-have keywords matched.")

    with gc2:
        st.markdown("#### Missing")
        missing_good = result.get(
            "missing_good_to_have_keywords", []
        )
        if missing_good:
            for keyword in missing_good:
                st.write(f"• {keyword}")
        else:
            st.write("No good-to-have keywords are missing.")

    # --------------------------------------------------------
    # Technical Skill Match detail  # NEW
    # --------------------------------------------------------

    st.subheader("Technical Skill Match Detail")

    st.caption(
        "This component only considers REQUIRED technical skills. "
        "Good-to-have skills are scored separately."
    )

    t1, t2, t3 = st.columns(3)

    with t1:
        st.metric("Technical Skill Match", f"{tech_score}%")

    with t2:
        st.metric(
            "Required Technical Skills",
            len(result.get("technical_matched_skills", []))
            + len(result.get("technical_partial_skills", []))
            + len(result.get("technical_missing_skills", []))
        )

    with t3:
        st.metric(
            "Good-to-Have Match",
            f"{good_to_have_score}%"
        )

    # --------------------------------------------------------
    # Skill Gap Analysis (deterministic)
    # --------------------------------------------------------

    st.subheader("Skill Gap Analysis")

    skill_gap = result.get("skill_gap", {})

    st.markdown("### 🔴 High-Priority Skill Gaps")
    high_priority = skill_gap.get("high_priority_gaps", [])
    if high_priority:
        for skill in high_priority:
            st.write(f"• {skill}")
    else:
        st.write("No major required skill gaps identified.")

    st.markdown("### 🟡 Partial / Related Skills")
    partial_gaps = skill_gap.get("partial_matches", [])
    if partial_gaps:
        for skill in partial_gaps:
            st.write(f"~ {skill}")
    else:
        st.write("No partial skill matches identified.")

    st.markdown("### 🔵 Good-to-Have Gaps")
    good_gaps = skill_gap.get("good_to_have_gaps", [])
    if good_gaps:
        for skill in good_gaps:
            st.write(f"• {skill}")
    else:
        st.write("No good-to-have gaps identified.")

    # --------------------------------------------------------
    # Required JD skill lists  # CHANGED (renamed labels)
    # --------------------------------------------------------

    st.subheader("Required JD Skills")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Matched JD Skills")
        matched = result.get("matched_skills", [])
        if matched:
            for skill in matched:
                st.write(f"✓ {skill}")
        else:
            st.write("No strong matches identified.")

    with col2:
        st.markdown("#### Missing JD Skills")
        missing = result.get("missing_skills", [])
        if missing:
            for skill in missing:
                st.write(f"• {skill}")
        else:
            st.write("No major missing skills identified.")

    st.markdown("#### Partial / Related Skills")
    partial = result.get("partial_match_skills", [])
    if partial:
        for skill in partial:
            st.write(f"~ {skill}")
    else:
        st.write("No partial matches identified.")

    # --------------------------------------------------------
    # LLM narrative
    # --------------------------------------------------------

    st.subheader("Candidate Summary")
    st.write(
        result.get("candidate_summary", "No summary available.")
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Strengths")
        strengths = result.get("strengths", [])
        if strengths:
            for item in strengths:
                st.write(f"✓ {item}")
        else:
            st.write("No strengths identified.")

    with col2:
        st.subheader("Weaknesses")
        weaknesses = result.get("weaknesses", [])
        if weaknesses:
            for item in weaknesses:
                st.write(f"• {item}")
        else:
            st.write("No weaknesses identified.")

    st.subheader("Experience Match")
    st.write(result.get("experience_match", "Not available."))

    st.subheader("Education Match")
    st.write(result.get("education_match", "Not available."))

    st.subheader("Project Match")
    st.write(result.get("project_match", "Not available."))

    st.subheader("Resume Improvement Recommendations")
    improvements = result.get("resume_improvements", [])
    if improvements:
        for index, item in enumerate(improvements, start=1):
            st.write(f"{index}. {item}")
    else:
        st.write("No improvement recommendations available.")

    st.subheader("AI-Generated Interview Questions")
    questions = result.get("interview_questions", [])
    if questions:
        for index, question in enumerate(questions, start=1):
            st.write(f"{index}. {question}")
    else:
        st.write("No interview questions generated.")

    with st.expander("Generate General Resume Improvement Tips"):
        if st.button("Generate Tips"):
            with st.spinner("Generating recommendations..."):
                try:
                    tips = generate_resume_tips(
                        st.session_state["resume_text"]
                    )
                    st.write(tips)
                except Exception as e:
                    st.error(f"Unable to generate tips: {e}")


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("AI Resume Analyzer | Python + Streamlit + Groq")