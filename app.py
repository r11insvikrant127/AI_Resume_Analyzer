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
    match_deterministic_skills
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
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Project Information")

    st.write(
        """
        This application uses Generative AI to compare a
        candidate's resume with a job description.
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

        Skill Match

        Skill Gaps

        Strengths

        Weaknesses

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
            # ================================================
            # EXTRACT RESUME TEXT
            # ================================================

            resume_text = extract_resume_text(uploaded_file)
            resume_text = clean_text(resume_text)

            if len(resume_text) < 100:
                st.error(
                    "Very little text was extracted from the PDF. "
                    "Please upload a text-based PDF."
                )
                st.stop()

            # ================================================
            # AI NARRATIVE ANALYSIS (no scoring, no skills)
            # ================================================

            result = analyze_resume(resume_text, job_description)

            # ================================================
            # AI KEYWORD EXTRACTION FROM JD
            # ================================================

            keyword_data = extract_keywords_from_jd(
                client, MODEL, job_description
            )

            required_keywords = keyword_data.get(
                "required_keywords", []
            )
            good_to_have_keywords = keyword_data.get(
                "good_to_have_keywords", []
            )

            # ================================================
            # DETERMINISTIC KEYWORD ANALYSIS
            # ================================================

            keyword_analysis = calculate_keyword_match(
                required_keywords,
                good_to_have_keywords,
                resume_text
            )

            # ================================================
            # DETERMINISTIC SKILL CLASSIFICATION
            # ================================================

            det = match_deterministic_skills(
                required_skills=required_keywords,
                good_to_have_skills=good_to_have_keywords,
                resume_text=resume_text
            )

            matched_skills = det["matched_skills"]
            partial_match_skills = det["partial_match_skills"]
            missing_skills = det["missing_skills"]

            # ================================================
            # DETERMINISTIC SKILL MATCH SCORE
            # ================================================

            skill_match_percentage = calculate_skill_match(
                matched_skills,
                missing_skills,
                partial_match_skills
            )

            # ================================================
            # DETERMINISTIC SKILL GAP ANALYSIS
            # ================================================

            skill_gap = build_skill_gap_analysis(
                matched_required=det["matched_required"],
                partial_required=det["partial_required"],
                missing_required=det["missing_required"],
                matched_good_to_have=det["matched_good_to_have"],
                partial_good_to_have=det["partial_good_to_have"],
                missing_good_to_have=det["missing_good_to_have"]
            )

            # ================================================
            # DETERMINISTIC ATS SCORE
            # ================================================

            ats_score = calculate_ats_score(
                keyword_analysis["required_percentage"],
                keyword_analysis["good_to_have_percentage"],
                skill_match_percentage
            )

            # ================================================
            # STORE RESULTS
            # ================================================

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

            result["matched_skills"] = matched_skills
            result["partial_match_skills"] = partial_match_skills
            result["missing_skills"] = missing_skills

            result["skill_match_percentage"] = skill_match_percentage
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
    # SCORE METRICS
    # --------------------------------------------------------

    score = result.get("ats_score", 0)
    skill_score = result.get("skill_match_percentage", 0)
    required_score = result.get("required_keyword_percentage", 0)
    good_to_have_score = result.get("good_to_have_percentage", 0)

    score_col1, score_col2, score_col3 = st.columns(3)

    with score_col1:
        st.metric("ATS Score", f"{score}%")

    with score_col2:
        st.metric("Skill Match", f"{skill_score}%")

    with score_col3:
        st.metric("Required Keyword Match", f"{required_score}%")

    st.progress(min(max(score, 0), 100) / 100)

    # --------------------------------------------------------
    # SCORE BREAKDOWN
    # --------------------------------------------------------

    st.subheader("ATS Score Breakdown")

    b1, b2, b3 = st.columns(3)

    with b1:
        st.metric("Required Keywords", f"{required_score}%")
        st.caption("Weight: 50%")

    with b2:
        st.metric("Skill Match", f"{skill_score}%")
        st.caption("Weight: 40%")

    with b3:
        st.metric("Good-to-Have", f"{good_to_have_score}%")
        st.caption("Weight: 10%")

    # --------------------------------------------------------
    # KEYWORD ANALYSIS
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
    # SKILL GAP ANALYSIS
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

    st.markdown("### 🟡 Partial / Needs More Evidence")
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
    # NARRATIVE SECTIONS (from LLM)
    # --------------------------------------------------------

    st.subheader("Candidate Summary")
    st.write(
        result.get(
            "candidate_summary",
            "No summary available."
        )
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Matched Skills")
        matched = result.get("matched_skills", [])
        if matched:
            for skill in matched:
                st.write(f"✓ {skill}")
        else:
            st.write("No strong matches identified.")

    with col2:
        st.subheader("Missing Skills")
        missing = result.get("missing_skills", [])
        if missing:
            for skill in missing:
                st.write(f"• {skill}")
        else:
            st.write("No major missing skills identified.")

    st.subheader("Partial Match Skills")
    partial = result.get("partial_match_skills", [])
    if partial:
        for skill in partial:
            st.write(f"~ {skill}")
    else:
        st.write("No partial matches identified.")

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