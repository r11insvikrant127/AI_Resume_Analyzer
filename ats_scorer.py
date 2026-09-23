# ============================================================
# TECHNICAL SKILL MATCH
# ============================================================

def calculate_skill_match(
    matched_technical_skills,
    missing_technical_skills,
    partial_technical_skills
):
    """
    Calculate the Technical Skill Match percentage.

    IMPORTANT:
    These lists MUST contain TECHNICAL skills only.

    Scoring:
        Full match    = 1.0
        Partial match = 0.5
        Missing       = 0.0

    Formula:

        Technical Skill Match =
            (
                matched
                + (partial × 0.5)
            )
            / total technical skills
            × 100

    Example:

        Matched  = 4
        Partial  = 2
        Missing  = 2

        Weighted score = 4 + (2 × 0.5)
                       = 5

        Total = 4 + 2 + 2
              = 8

        Technical Skill Match
            = 5 / 8 × 100
            = 62.5
            ≈ 63%
    """

    matched_count = len(
        matched_technical_skills
    )

    partial_count = len(
        partial_technical_skills
    )

    missing_count = len(
        missing_technical_skills
    )

    total_technical_skills = (
        matched_count
        + partial_count
        + missing_count
    )

    # Avoid division by zero when the JD contains
    # no technical skills.
    if total_technical_skills == 0:
        return 0

    weighted_score = (
        matched_count
        + (partial_count * 0.5)
    )

    technical_skill_percentage = (
        weighted_score
        / total_technical_skills
        * 100
    )

    return round(
        technical_skill_percentage
    )


# ============================================================
# FINAL ATS SCORE
# ============================================================

def calculate_ats_score(
    required_keyword_percentage,
    technical_skill_percentage,
    good_to_have_percentage
):
    """
    Calculate the final deterministic ATS score.

    Components:

        Required Keyword Match = 50%
        Technical Skill Match  = 40%
        Good-to-Have Match     = 10%

    Formula:

        ATS Score =
            (Required Keyword Match × 0.50)
            +
            (Technical Skill Match × 0.40)
            +
            (Good-to-Have Match × 0.10)
    """

    ats_score = (
        required_keyword_percentage * 0.50
        + technical_skill_percentage * 0.40
        + good_to_have_percentage * 0.10
    )

    return round(
        ats_score
    )