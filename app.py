import os
import json
import re

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from resume_parser import (
    extract_resume_text,
    clean_resume_text
)

from keyword_analyzer import (
    extract_keywords_from_jd,
    compare_requirements_with_resume,
    organize_match_results
)

from ats_scorer import (
    calculate_requirement_match_percentage,
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

client = Groq(
    api_key=API_KEY
)

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
# LLM QUALITATIVE ANALYSIS
# ============================================================

def analyze_resume(
    resume_text,
    job_description
):
    """
    Use the LLM for qualitative resume analysis.

    Numerical ATS scoring is NOT performed here.

    The LLM provides:

        - candidate summary
        - strengths
        - weaknesses
        - experience analysis
        - education analysis
        - project analysis
        - resume improvements
        - interview questions
    """

    prompt = f"""
You are an expert resume analyst.

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

2. Do not assume a skill that is not supported by
   the resume.

3. Base the analysis only on the provided resume
   and job description.

4. interview_questions should contain 10 relevant
   questions.

5. Keep the answer concise but useful.

6. Do not calculate or invent an ATS score.

7. Do not fabricate achievements or metrics.

8. Return JSON only.

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
                    "You are a professional resume analyst. "
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

    content = (
        response
        .choices[0]
        .message
        .content
        or ""
    )

    return parse_json_response(
        content
    )


# ============================================================
# JSON PARSER
# ============================================================

def parse_json_response(content):
    """
    Parse JSON returned by the LLM.

    Also handles responses accidentally wrapped
    in Markdown code fences.
    """

    content = content.strip()

    content = re.sub(
        r"^```json\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = re.sub(
        r"^```\s*",
        "",
        content
    )

    content = re.sub(
        r"\s*```$",
        "",
        content
    )

    try:

        return json.loads(
            content
        )

    except json.JSONDecodeError:

        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1:

            try:

                return json.loads(
                    content[
                        start:end + 1
                    ]
                )

            except json.JSONDecodeError as exc:

                raise ValueError(
                    "The AI returned an invalid JSON response."
                ) from exc

        raise ValueError(
            "The AI returned an invalid response. "
            "Please try again."
        )


# ============================================================
# GENERAL RESUME TIPS
# ============================================================

def generate_resume_tips(resume_text):
    """
    Generate general resume-improvement suggestions.

    The model is explicitly instructed not to invent
    achievements or numerical metrics.
    """

    prompt = f"""
Review this resume as a professional resume coach.

Provide 8 practical recommendations to improve it.

Focus on:

- ATS compatibility
- Skills presentation
- Project descriptions
- Achievement statements
- Keywords
- Formatting
- Quantifiable results
- Professional summary

IMPORTANT:

1. Do NOT invent achievements.

2. Do NOT fabricate numbers.

3. Do NOT estimate metrics.

4. Do NOT suggest adding fake percentages,
   fake user counts, fake performance improvements,
   fake revenue, fake rankings, or fake impact.

5. If the resume does not contain measurable results,
   recommend adding real metrics only when the candidate
   can verify them.

6. Recommendations must be based on the actual resume.

Resume:

{resume_text}

Return only a numbered list.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert resume coach. "
                    "Never invent or fabricate candidate "
                    "achievements or metrics."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return (
        response
        .choices[0]
        .message
        .content
        or ""
    )


# ============================================================
# CACHED JD SKILL EXTRACTION
# ============================================================

def get_jd_keywords(job_description):
    """
    Cache JD requirement extraction for the current
    Streamlit session.
    """

    cache = st.session_state.setdefault(
        "jd_keyword_cache",
        {}
    )

    key = job_description.strip()

    if key in cache:

        return cache[key]

    requirement_data = extract_keywords_from_jd(
        client,
        MODEL,
        job_description
    )

    cache[key] = requirement_data

    return requirement_data


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "Project Information"
    )

    st.write(
        """
        This application uses Generative AI for semantic
        job-description analysis, resume matching, and
        qualitative resume analysis.

        Python performs the numerical ATS calculations.
        """
    )

    st.divider()

    st.subheader(
        "Technology"
    )

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

    st.subheader(
        "Analysis"
    )

    st.write(
        """
        ATS Score

        Requirement Matching

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

    st.subheader(
        "1. Upload Resume"
    )

    uploaded_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"]
    )


with col2:

    st.subheader(
        "2. Job Description"
    )

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

    # --------------------------------------------------------
    # Validate inputs
    # --------------------------------------------------------

    if uploaded_file is None:

        st.warning(
            "Please upload a resume PDF."
        )

        st.stop()

    if not job_description.strip():

        st.warning(
            "Please enter a job description."
        )

        st.stop()


    with st.spinner(
        "Reading and analyzing resume..."
    ):

        try:

            # =================================================
            # 1. EXTRACT RESUME TEXT
            # =================================================

            resume_text = extract_resume_text(
                uploaded_file
            )

            resume_text = clean_resume_text(
                resume_text
            )

            if len(resume_text) < 100:

                st.error(
                    "Very little text was extracted from "
                    "the PDF. Please upload a text-based PDF."
                )

                st.stop()


            # =================================================
            # 2. LLM QUALITATIVE ANALYSIS
            # =================================================

            result = analyze_resume(
                resume_text,
                job_description
            )


            # =================================================
            # 3. EXTRACT STRUCTURED JD REQUIREMENTS
            # =================================================

            requirement_data = get_jd_keywords(
                job_description
            )

            required_skills = requirement_data.get(
                "required_skills",
                []
            )

            good_to_have_skills = requirement_data.get(
                "good_to_have_skills",
                []
            )


            # =================================================
            # 4. SEMANTIC REQUIREMENT MATCHING
            # =================================================

            required_matches = compare_requirements_with_resume(
                client=client,
                model=MODEL,
                requirements=required_skills,
                resume_text=resume_text
            )

            good_to_have_matches = compare_requirements_with_resume(
                client=client,
                model=MODEL,
                requirements=good_to_have_skills,
                resume_text=resume_text
            )


            # =================================================
            # 5. ORGANIZE MATCH RESULTS
            # =================================================

            det = organize_match_results(
                required_matches=required_matches,
                good_to_have_matches=good_to_have_matches
            )


            # =================================================
            # 6. REQUIREMENT MATCH SCORES
            # =================================================

            required_match_percentage = (
                calculate_requirement_match_percentage(
                    required_matches
                )
            )

            good_to_have_match_percentage = (
                calculate_requirement_match_percentage(
                    good_to_have_matches
                )
            )


            # =================================================
            # 7. TECHNICAL REQUIREMENT MATCHES
            # =================================================
            #
            # Category information comes from the structured
            # semantic requirement result.
            #
            # No hardcoded technology list is used.
            # =================================================

            technical_matches = [
                match
                for match in required_matches
                if str(
                    match.get(
                        "category",
                        ""
                    )
                ).strip().lower() == "technical"
            ]


            # =================================================
            # 8. TECHNICAL SKILL MATCH
            # =================================================

            technical_skill_percentage = (
                calculate_skill_match(
                    technical_matches
                )
            )


            # =================================================
            # 9. TECHNICAL MATCHED / PARTIAL / MISSING
            # =================================================

            technical_matched = [
                match.get(
                    "requirement",
                    ""
                )
                for match in technical_matches
                if match.get(
                    "status"
                ) == "matched"
            ]

            technical_partial = [
                match.get(
                    "requirement",
                    ""
                )
                for match in technical_matches
                if match.get(
                    "status"
                ) == "partial"
            ]

            technical_missing = [
                match.get(
                    "requirement",
                    ""
                )
                for match in technical_matches
                if match.get(
                    "status"
                ) == "missing"
            ]


            # =================================================
            # 10. NON-TECHNICAL REQUIREMENT MATCHES
            # =================================================

            required_non_technical_matches = [
                match
                for match in required_matches
                if str(
                    match.get(
                        "category",
                        ""
                    )
                ).strip().lower() != "technical"
            ]


            non_technical_matched = [
                match.get(
                    "requirement",
                    ""
                )
                for match in required_non_technical_matches
                if match.get(
                    "status"
                ) == "matched"
            ]

            non_technical_partial = [
                match.get(
                    "requirement",
                    ""
                )
                for match in required_non_technical_matches
                if match.get(
                    "status"
                ) == "partial"
            ]

            non_technical_missing = [
                match.get(
                    "requirement",
                    ""
                )
                for match in required_non_technical_matches
                if match.get(
                    "status"
                ) == "missing"
            ]


            # =================================================
            # 11. SKILL GAP ANALYSIS
            # =================================================

            skill_gap = build_skill_gap_analysis(
                matched_required=det[
                    "matched_required"
                ],
                partial_required=det[
                    "partial_required"
                ],
                missing_required=det[
                    "missing_required"
                ],
                matched_good_to_have=det[
                    "matched_good_to_have"
                ],
                partial_good_to_have=det[
                    "partial_good_to_have"
                ],
                missing_good_to_have=det[
                    "missing_good_to_have"
                ]
            )


            # =================================================
            # 12. FINAL ATS SCORE
            # =================================================

            ats_score = calculate_ats_score(
                required_match_percentage,
                technical_skill_percentage,
                good_to_have_match_percentage
            )


            # =================================================
            # 13. STORE JD REQUIREMENTS
            # =================================================

            result["required_skills"] = (
                required_skills
            )

            result["good_to_have_skills"] = (
                good_to_have_skills
            )


            # =================================================
            # 14. STORE REQUIREMENT MATCH RESULTS
            # =================================================

            result["matched_required_requirements"] = (
                det["matched_required"]
            )

            result["partial_required_requirements"] = (
                det["partial_required"]
            )

            result["missing_required_requirements"] = (
                det["missing_required"]
            )

            result["matched_good_to_have_requirements"] = (
                det["matched_good_to_have"]
            )

            result["partial_good_to_have_requirements"] = (
                det["partial_good_to_have"]
            )

            result["missing_good_to_have_requirements"] = (
                det["missing_good_to_have"]
            )


            # =================================================
            # 15. STORE REQUIREMENT SCORES
            # =================================================

            result["required_match_percentage"] = (
                required_match_percentage
            )

            result["good_to_have_match_percentage"] = (
                good_to_have_match_percentage
            )


            # =================================================
            # 16. STORE TECHNICAL SKILL DATA
            # =================================================

            result["technical_matched_skills"] = (
                technical_matched
            )

            result["technical_partial_skills"] = (
                technical_partial
            )

            result["technical_missing_skills"] = (
                technical_missing
            )

            result["technical_skill_percentage"] = (
                technical_skill_percentage
            )


            # =================================================
            # 17. STORE NON-TECHNICAL DATA
            # =================================================

            result["required_non_technical_skills"] = [
                match.get(
                    "requirement",
                    ""
                )
                for match in required_non_technical_matches
            ]

            result["non_technical_matched_skills"] = (
                non_technical_matched
            )

            result["non_technical_partial_skills"] = (
                non_technical_partial
            )

            result["non_technical_missing_skills"] = (
                non_technical_missing
            )


            # =================================================
            # 18. STORE GENERAL REQUIRED SKILL DATA
            # =================================================

            result["matched_skills"] = (
                det["matched_required"]
            )

            result["partial_match_skills"] = (
                det["partial_required"]
            )

            result["missing_skills"] = (
                det["missing_required"]
            )


            # =================================================
            # 19. STORE FINAL RESULTS
            # =================================================

            result["skill_match_percentage"] = (
                technical_skill_percentage
            )

            result["ats_score"] = (
                ats_score
            )

            result["skill_gap"] = (
                skill_gap
            )


            # =================================================
            # 20. SAVE TO STREAMLIT SESSION
            # =================================================

            st.session_state["analysis"] = (
                result
            )

            st.session_state["resume_text"] = (
                resume_text
            )

            st.session_state["job_description"] = (
                job_description
            )


            st.success(
                "Resume analysis completed successfully!"
            )


        except Exception as e:

            st.error(
                f"Analysis failed: {e}"
            )


# ============================================================
# DISPLAY RESULTS
# ============================================================

if "analysis" in st.session_state:

    result = st.session_state[
        "analysis"
    ]

    st.divider()

    st.header(
        "Resume Analysis Report"
    )


    # ========================================================
    # HEADLINE METRICS
    # ========================================================

    score = result.get(
        "ats_score",
        0
    )

    required_score = result.get(
        "required_match_percentage",
        0
    )

    technical_score = result.get(
        "technical_skill_percentage",
        0
    )

    good_to_have_score = result.get(
        "good_to_have_match_percentage",
        0
    )


    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "ATS Score",
            f"{score}%"
        )

    with c2:

        st.metric(
            "Required Requirement Match",
            f"{required_score}%"
        )

    with c3:

        st.metric(
            "Technical Skill Match",
            f"{technical_score}%"
        )


    st.progress(
        min(
            max(score, 0),
            100
        ) / 100
    )


    # ========================================================
    # SCORE CALCULATION
    # ========================================================

    st.subheader(
        "How This ATS Score Was Calculated"
    )

    req_contribution = round(
        required_score * 0.50,
        2
    )

    technical_contribution = round(
        technical_score * 0.40,
        2
    )

    good_to_have_contribution = round(
        good_to_have_score * 0.10,
        2
    )

    st.markdown(
        f"""
<div class="formula">

Required Requirement Match :
{required_score}% × 0.50 = {req_contribution}

<br>

Technical Skill Match :
{technical_score}% × 0.40 = {technical_contribution}

<br>

Good-to-Have Match :
{good_to_have_score}% × 0.10 = {good_to_have_contribution}

<hr>

<b>Final ATS Score = {score}%</b>

</div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # REQUIREMENT ANALYSIS
    # ========================================================

    st.subheader(
        "Job Requirement Analysis"
    )

    r1, r2, r3 = st.columns(3)

    with r1:

        st.metric(
            "Required Match",
            f"{required_score}%"
        )

    with r2:

        st.metric(
            "Good-to-Have Match",
            f"{good_to_have_score}%"
        )

    with r3:

        overall_requirement_score = round(
            (
                required_score
                + good_to_have_score
            ) / 2
        )

        st.metric(
            "Overall Requirement Match",
            f"{overall_requirement_score}%"
        )


    # ========================================================
    # REQUIRED REQUIREMENTS
    # ========================================================

    st.markdown(
        "### Required Requirements"
    )

    rc1, rc2, rc3 = st.columns(3)

    with rc1:

        st.markdown(
            "#### Matched"
        )

        matched_required = result.get(
            "matched_required_requirements",
            []
        )

        if matched_required:

            for requirement in matched_required:

                st.write(
                    f"✓ {requirement}"
                )

        else:

            st.write(
                "No required requirements matched."
            )


    with rc2:

        st.markdown(
            "#### Partial"
        )

        partial_required = result.get(
            "partial_required_requirements",
            []
        )

        if partial_required:

            for requirement in partial_required:

                st.write(
                    f"~ {requirement}"
                )

        else:

            st.write(
                "No partial required matches."
            )


    with rc3:

        st.markdown(
            "#### Missing"
        )

        missing_required = result.get(
            "missing_required_requirements",
            []
        )

        if missing_required:

            for requirement in missing_required:

                st.write(
                    f"• {requirement}"
                )

        else:

            st.write(
                "No required requirements are missing."
            )


    # ========================================================
    # GOOD-TO-HAVE REQUIREMENTS
    # ========================================================

    st.markdown(
        "### Good-to-Have Requirements"
    )

    gc1, gc2, gc3 = st.columns(3)

    with gc1:

        st.markdown(
            "#### Matched"
        )

        matched_good = result.get(
            "matched_good_to_have_requirements",
            []
        )

        if matched_good:

            for requirement in matched_good:

                st.write(
                    f"✓ {requirement}"
                )

        else:

            st.write(
                "No good-to-have requirements matched."
            )


    with gc2:

        st.markdown(
            "#### Partial"
        )

        partial_good = result.get(
            "partial_good_to_have_requirements",
            []
        )

        if partial_good:

            for requirement in partial_good:

                st.write(
                    f"~ {requirement}"
                )

        else:

            st.write(
                "No partial good-to-have matches."
            )


    with gc3:

        st.markdown(
            "#### Missing"
        )

        missing_good = result.get(
            "missing_good_to_have_requirements",
            []
        )

        if missing_good:

            for requirement in missing_good:

                st.write(
                    f"• {requirement}"
                )

        else:

            st.write(
                "No good-to-have requirements are missing."
            )


    # ========================================================
    # TECHNICAL SKILL MATCH DETAIL
    # ========================================================

    st.subheader(
        "Technical Skill Match Detail"
    )

    st.caption(
        "This component considers required technical "
        "skills only. Categories are determined from "
        "the job description."
    )

    technical_matched = result.get(
        "technical_matched_skills",
        []
    )

    technical_partial = result.get(
        "technical_partial_skills",
        []
    )

    technical_missing = result.get(
        "technical_missing_skills",
        []
    )

    total_technical_skills = (
        len(technical_matched)
        + len(technical_partial)
        + len(technical_missing)
    )

    t1, t2 = st.columns(2)

    with t1:

        st.metric(
            "Technical Skill Match",
            f"{technical_score}%"
        )

    with t2:

        st.metric(
            "Required Technical Skills",
            total_technical_skills
        )


    # ========================================================
    # TECHNICAL SKILL BREAKDOWN
    # ========================================================

    tc1, tc2, tc3 = st.columns(3)

    with tc1:

        st.markdown(
            "#### Matched Technical"
        )

        if technical_matched:

            for skill in technical_matched:

                st.write(
                    f"✓ {skill}"
                )

        else:

            st.write(
                "None"
            )


    with tc2:

        st.markdown(
            "#### Partial Technical"
        )

        if technical_partial:

            for skill in technical_partial:

                st.write(
                    f"~ {skill}"
                )

        else:

            st.write(
                "None"
            )


    with tc3:

        st.markdown(
            "#### Missing Technical"
        )

        if technical_missing:

            for skill in technical_missing:

                st.write(
                    f"• {skill}"
                )

        else:

            st.write(
                "None"
            )


    # ========================================================
    # NON-TECHNICAL REQUIREMENTS
    # ========================================================

    st.subheader(
        "Other Required Skills"
    )

    st.caption(
        "These requirements are part of the job description "
        "but are not included in the Technical Skill Match."
    )

    required_non_technical = result.get(
        "required_non_technical_skills",
        []
    )

    non_technical_matched = result.get(
        "non_technical_matched_skills",
        []
    )

    non_technical_partial = result.get(
        "non_technical_partial_skills",
        []
    )

    non_technical_missing = result.get(
        "non_technical_missing_skills",
        []
    )

    if required_non_technical:

        for skill in required_non_technical:

            if skill in non_technical_matched:

                st.write(
                    f"✓ {skill}"
                )

            elif skill in non_technical_partial:

                st.write(
                    f"~ {skill}"
                )

            elif skill in non_technical_missing:

                st.write(
                    f"• {skill}"
                )

    else:

        st.write(
            "No non-technical or foundational requirements "
            "were identified."
        )


    # ========================================================
    # SKILL GAP ANALYSIS
    # ========================================================

    st.subheader(
        "Skill Gap Analysis"
    )

    skill_gap = result.get(
        "skill_gap",
        {}
    )


    # --------------------------------------------------------
    # High priority
    # --------------------------------------------------------

    st.markdown(
        "### 🔴 High-Priority Skill Gaps"
    )

    high_priority = skill_gap.get(
        "high_priority_gaps",
        []
    )

    if high_priority:

        for skill in high_priority:

            st.write(
                f"• {skill}"
            )

    else:

        st.write(
            "No major required skill gaps identified."
        )


    # --------------------------------------------------------
    # Partial required
    # --------------------------------------------------------

    st.markdown(
        "### 🟡 Partial Required Skills"
    )

    partial_gaps = skill_gap.get(
        "partial_matches",
        []
    )

    if partial_gaps:

        for skill in partial_gaps:

            st.write(
                f"~ {skill}"
            )

    else:

        st.write(
            "No partial required-skill matches identified."
        )


    # --------------------------------------------------------
    # Good-to-have gaps
    # --------------------------------------------------------

    st.markdown(
        "### 🔵 Good-to-Have Gaps"
    )

    good_gaps = skill_gap.get(
        "good_to_have_gaps",
        []
    )

    if good_gaps:

        for skill in good_gaps:

            st.write(
                f"• {skill}"
            )

    else:

        st.write(
            "No good-to-have gaps identified."
        )


    # ========================================================
    # CANDIDATE SUMMARY
    # ========================================================

    st.subheader(
        "Candidate Summary"
    )

    st.write(
        result.get(
            "candidate_summary",
            "No summary available."
        )
    )


    # ========================================================
    # STRENGTHS / WEAKNESSES
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Strengths"
        )

        strengths = result.get(
            "strengths",
            []
        )

        if strengths:

            for item in strengths:

                st.write(
                    f"✓ {item}"
                )

        else:

            st.write(
                "No strengths identified."
            )


    with col2:

        st.subheader(
            "Weaknesses"
        )

        weaknesses = result.get(
            "weaknesses",
            []
        )

        if weaknesses:

            for item in weaknesses:

                st.write(
                    f"• {item}"
                )

        else:

            st.write(
                "No weaknesses identified."
            )


    # ========================================================
    # EXPERIENCE MATCH
    # ========================================================

    st.subheader(
        "Experience Match"
    )

    st.write(
        result.get(
            "experience_match",
            "Not available."
        )
    )


    # ========================================================
    # EDUCATION MATCH
    # ========================================================

    st.subheader(
        "Education Match"
    )

    st.write(
        result.get(
            "education_match",
            "Not available."
        )
    )


    # ========================================================
    # PROJECT MATCH
    # ========================================================

    st.subheader(
        "Project Match"
    )

    st.write(
        result.get(
            "project_match",
            "Not available."
        )
    )


    # ========================================================
    # RESUME IMPROVEMENTS
    # ========================================================

    st.subheader(
        "Resume Improvement Recommendations"
    )

    improvements = result.get(
        "resume_improvements",
        []
    )

    if improvements:

        for index, item in enumerate(
            improvements,
            start=1
        ):

            st.write(
                f"{index}. {item}"
            )

    else:

        st.write(
            "No improvement recommendations available."
        )


    # ========================================================
    # INTERVIEW QUESTIONS
    # ========================================================

    st.subheader(
        "AI-Generated Interview Questions"
    )

    questions = result.get(
        "interview_questions",
        []
    )

    if questions:

        for index, question in enumerate(
            questions,
            start=1
        ):

            st.write(
                f"{index}. {question}"
            )

    else:

        st.write(
            "No interview questions generated."
        )


    # ========================================================
    # GENERAL RESUME TIPS
    # ========================================================

    with st.expander(
        "Generate General Resume Improvement Tips"
    ):

        if st.button(
            "Generate Tips"
        ):

            with st.spinner(
                "Generating recommendations..."
            ):

                try:

                    tips = generate_resume_tips(
                        st.session_state[
                            "resume_text"
                        ]
                    )

                    st.write(
                        tips
                    )

                except Exception as e:

                    st.error(
                        f"Unable to generate tips: {e}"
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Resume Analyzer | Python + Streamlit + Groq"
)