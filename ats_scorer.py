# ============================================================
# SKILL MATCH
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

    Inputs come from
    keyword_analyzer.match_deterministic_skills().
    """

    matched_count = len(matched_skills)
    missing_count = len(missing_skills)
    partial_count = len(partial_match_skills)

    total_skills = (
        matched_count
        + missing_count
        + partial_count
    )

    if total_skills == 0:
        return 0

    weighted_score = matched_count + (partial_count * 0.5)

    return round(weighted_score / total_skills * 100)


# ============================================================
# ATS SCORE
# ============================================================

def calculate_ats_score(
    required_keyword_percentage,
    good_to_have_percentage,
    skill_match_percentage
):
    """
    Final deterministic ATS score.

    Required keywords = 50%
    Skills            = 40%
    Good-to-have      = 10%
    """

    ats_score = (
        required_keyword_percentage * 0.50
        + skill_match_percentage * 0.40
        + good_to_have_percentage * 0.10
    )

    return round(ats_score)