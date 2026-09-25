# analysis_pipeline.py

from resume_parser import extract_resume_text, clean_resume_text

from keyword_analyzer import (
    compare_requirements_with_resume,
    organize_match_results,
)

from ats_scorer import (
    calculate_requirement_match_percentage,
    calculate_skill_match,
    calculate_ats_score,
)

from skill_gap_analyzer import build_skill_gap_analysis

from ats_keyword_analyzer import analyze_ats_keywords


def analyze_single_resume(
    uploaded_file,
    job_description,
    requirement_data,
    analyze_resume_llm,
    client,
    model,
):
    """
    Run the full ATS pipeline for one resume against a
    pre-extracted job description requirement set.

    Returns a dict with everything app.py displays, plus:
        - ats_keyword_analysis   (Feature 1)
        - resume_name, resume_text
    """

    resume_text = extract_resume_text(uploaded_file)
    resume_text = clean_resume_text(resume_text)

    if len(resume_text) < 100:
        raise ValueError(
            "Very little text was extracted from this file."
        )

    # 1. LLM qualitative analysis
    result = analyze_resume_llm(resume_text, job_description)

    # 2. Requirement lists
    required_skills = requirement_data.get("required_skills", [])
    good_to_have_skills = requirement_data.get("good_to_have_skills", [])

    # 3. Semantic matching
    required_matches = compare_requirements_with_resume(
        client=client,
        model=model,
        requirements=required_skills,
        resume_text=resume_text,
    )

    good_to_have_matches = compare_requirements_with_resume(
        client=client,
        model=model,
        requirements=good_to_have_skills,
        resume_text=resume_text,
    )

    det = organize_match_results(
        required_matches=required_matches,
        good_to_have_matches=good_to_have_matches,
    )

    # 4. Scores
    required_match_percentage = calculate_requirement_match_percentage(
        required_matches
    )
    good_to_have_match_percentage = calculate_requirement_match_percentage(
        good_to_have_matches
    )

    technical_matches = [
        m for m in required_matches
        if str(m.get("category", "")).strip().lower() == "technical"
    ]
    technical_skill_percentage = calculate_skill_match(technical_matches)

    ats_score = calculate_ats_score(
        required_match_percentage,
        technical_skill_percentage,
        good_to_have_match_percentage,
    )

    # 5. Skill gap
    skill_gap = build_skill_gap_analysis(
        matched_required=det["matched_required"],
        partial_required=det["partial_required"],
        missing_required=det["missing_required"],
        matched_good_to_have=det["matched_good_to_have"],
        partial_good_to_have=det["partial_good_to_have"],
        missing_good_to_have=det["missing_good_to_have"],
    )

    # 6. Attach everything app.py already displays
    result["required_skills"] = required_skills
    result["good_to_have_skills"] = good_to_have_skills

    result["matched_required_requirements"] = det["matched_required"]
    result["partial_required_requirements"] = det["partial_required"]
    result["missing_required_requirements"] = det["missing_required"]
    result["matched_good_to_have_requirements"] = det["matched_good_to_have"]
    result["partial_good_to_have_requirements"] = det["partial_good_to_have"]
    result["missing_good_to_have_requirements"] = det["missing_good_to_have"]

    result["required_match_percentage"] = required_match_percentage
    result["good_to_have_match_percentage"] = good_to_have_match_percentage

    technical_matched = [
        m.get("requirement", "") for m in technical_matches
        if m.get("status") == "matched"
    ]
    technical_partial = [
        m.get("requirement", "") for m in technical_matches
        if m.get("status") == "partial"
    ]
    technical_missing = [
        m.get("requirement", "") for m in technical_matches
        if m.get("status") == "missing"
    ]

    result["technical_matched_skills"] = technical_matched
    result["technical_partial_skills"] = technical_partial
    result["technical_missing_skills"] = technical_missing
    result["technical_skill_percentage"] = technical_skill_percentage

    required_non_technical_matches = [
        m for m in required_matches
        if str(m.get("category", "")).strip().lower() != "technical"
    ]

    result["required_non_technical_skills"] = [
        m.get("requirement", "") for m in required_non_technical_matches
    ]
    result["non_technical_matched_skills"] = [
        m.get("requirement", "") for m in required_non_technical_matches
        if m.get("status") == "matched"
    ]
    result["non_technical_partial_skills"] = [
        m.get("requirement", "") for m in required_non_technical_matches
        if m.get("status") == "partial"
    ]
    result["non_technical_missing_skills"] = [
        m.get("requirement", "") for m in required_non_technical_matches
        if m.get("status") == "missing"
    ]

    result["matched_skills"] = det["matched_required"]
    result["partial_match_skills"] = det["partial_required"]
    result["missing_skills"] = det["missing_required"]

    result["skill_match_percentage"] = technical_skill_percentage
    result["ats_score"] = ats_score
    result["skill_gap"] = skill_gap

    # 7. ATS keyword analysis (Feature 1)
    result["ats_keyword_analysis"] = analyze_ats_keywords(
        resume_text=resume_text,
        required_skills=required_skills,
        good_to_have_skills=good_to_have_skills,
    )

    result["resume_name"] = getattr(uploaded_file, "name", "resume")
    result["resume_text"] = resume_text

    return result