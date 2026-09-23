# ============================================================
# SKILL MATCH (used for the Technical Skill component)
# ============================================================

def calculate_skill_match(
    matched_skills,
    missing_skills,
    partial_match_skills
):
    """
    Deterministic skill-match percentage.

    Full match    = 1.0
    Partial match = 0.5
    Missing       = 0.0

    Inputs MUST be the TECHNICAL-only classification lists,
    produced by:
        keyword_analyzer.split_technical_skills(...)
        keyword_analyzer.match_deterministic_skills(...)
    """

    matched_count = len(matched_skills)
    missing_count = len(missing_skills)
    partial_count = len(partial_match_skills)

    total = matched_count + missing_count + partial_count

    if total == 0:
        return 0

    weighted = matched_count + (partial_count * 0.5)

    return round(weighted / total * 100)


# ============================================================
# ATS SCORE
# ============================================================

def calculate_ats_score(
    required_keyword_percentage,
    technical_skill_percentage,
    good_to_have_percentage
):
    """
    Final deterministic ATS score.

    Components:
        Required Keyword Match  (all required keywords)     50%
        Technical Skill Match   (required technical only)   40%
        Good-to-Have Match      (optional keywords)         10%
    """

    ats_score = (
        required_keyword_percentage * 0.50
        + technical_skill_percentage * 0.40
        + good_to_have_percentage * 0.10
    )

    return round(ats_score)