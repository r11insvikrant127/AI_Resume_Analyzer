# ============================================================
# SEMANTIC REQUIREMENT SCORE
# ============================================================

def calculate_requirement_match_percentage(
    matches
):
    """
    Calculate the average semantic match strength.

    Each match must contain:

        match_strength

    where:

        1.0 = strong/direct evidence
        0.0 = no evidence

    The LLM determines the evidence strength.
    Python performs only the arithmetic.
    """

    if not matches:
        return 0

    strengths = []

    for match in matches:

        if not isinstance(match, dict):
            continue

        try:

            strength = float(
                match.get(
                    "match_strength",
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            strength = 0.0

        # Keep the value mathematically valid.

        strength = max(
            0.0,
            min(
                1.0,
                strength
            )
        )

        strengths.append(
            strength
        )

    if not strengths:
        return 0

    average_strength = (
        sum(strengths)
        / len(strengths)
    )

    return round(
        average_strength * 100
    )


# ============================================================
# TECHNICAL REQUIREMENT SCORE
# ============================================================

def calculate_skill_match(
    technical_matches
):
    """
    Calculate the technical skill match percentage.

    Only technical requirements should be passed here.

    Each requirement contains a semantic match_strength
    between 0 and 1.

    Example:

        Python       -> 1.0
        REST APIs    -> 0.8
        Kubernetes   -> 0.0

    Technical Skill Match:

        (1.0 + 0.8 + 0.0) / 3 × 100
        = 60%
    """

    return calculate_requirement_match_percentage(
        technical_matches
    )


# ============================================================
# FINAL ATS SCORE
# ============================================================

def calculate_ats_score(
    required_match_percentage,
    technical_skill_percentage,
    good_to_have_percentage
):
    """
    Calculate the final ATS score.

    Components:

        Required Requirement Match = 50%
        Technical Skill Match       = 40%
        Good-to-Have Match          = 10%

    Python performs the arithmetic only.

    No skill names, aliases, technology relationships,
    or domain-specific rules are hardcoded here.
    """

    ats_score = (
        required_match_percentage * 0.50
        + technical_skill_percentage * 0.40
        + good_to_have_percentage * 0.10
    )

    return round(
        ats_score
    )