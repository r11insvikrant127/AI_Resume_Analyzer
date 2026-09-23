# ============================================================
# SKILL GAP ANALYZER
# ============================================================
#
# Pure presenter of the deterministic classification produced
# by:
#
#     keyword_analyzer.match_deterministic_skills()
#
# This module does NOT consult the LLM.
#
#
# DETERMINISTIC PRIORITY RULES
# ============================================================
#
# REQUIRED SKILLS
#
#     matched
#         -> Not a gap
#
#     partial
#         -> Partial / Related
#
#     missing
#         -> High Priority Gap
#
#
# GOOD-TO-HAVE SKILLS
#
#     matched
#         -> Not a gap
#
#     partial
#         -> Good-to-Have Gap
#
#     missing
#         -> Good-to-Have Gap
#
#
# IMPORTANT
# ============================================================
#
# Good-to-have skills are optional.
#
# Therefore, even when a good-to-have skill has a related
# technology in the resume, it should NOT appear in the main
# "Partial / Related" section.
#
# It belongs under "Good-to-Have Gaps".
# ============================================================


def build_skill_gap_analysis(
    matched_required,
    partial_required,
    missing_required,
    matched_good_to_have,
    partial_good_to_have,
    missing_good_to_have
):
    """
    Build deterministic skill-gap categories.

    Parameters
    ----------
    matched_required : list
        Required skills directly matched in the resume.

    partial_required : list
        Required skills for which an explicitly related
        technology/skill was found.

    missing_required : list
        Required skills for which neither the exact skill
        nor an explicitly related skill was found.

    matched_good_to_have : list
        Optional skills directly matched in the resume.

    partial_good_to_have : list
        Optional skills for which an explicitly related
        technology/skill was found.

    missing_good_to_have : list
        Optional skills for which neither the exact skill
        nor an explicitly related skill was found.


    Returns
    -------
    dict
        Deterministic skill-gap analysis suitable for
        presentation in the Streamlit UI.
    """

    # ========================================================
    # REQUIRED SKILLS
    # ========================================================

    matched_required = list(
        matched_required or []
    )

    partial_required = list(
        partial_required or []
    )

    missing_required = list(
        missing_required or []
    )

    # Missing REQUIRED skills are high-priority gaps.
    high_priority_gaps = missing_required

    # Partial REQUIRED skills are related but not exact.
    partial_matches = partial_required


    # ========================================================
    # GOOD-TO-HAVE SKILLS
    # ========================================================

    matched_good_to_have = list(
        matched_good_to_have or []
    )

    partial_good_to_have = list(
        partial_good_to_have or []
    )

    missing_good_to_have = list(
        missing_good_to_have or []
    )

    # Both missing and partial optional skills belong to the
    # Good-to-Have Gap category.
    good_to_have_gaps = (
        partial_good_to_have
        + missing_good_to_have
    )


    # ========================================================
    # RETURN STRUCTURED RESULT
    # ========================================================

    return {

        # ----------------------------------------------------
        # Required skills
        # ----------------------------------------------------

        "matched_required":
            matched_required,

        "partial_required":
            partial_required,

        "high_priority_gaps":
            high_priority_gaps,

        "partial_matches":
            partial_matches,

        # ----------------------------------------------------
        # Good-to-have skills
        # ----------------------------------------------------

        "matched_good_to_have":
            matched_good_to_have,

        "partial_good_to_have":
            partial_good_to_have,

        "good_to_have_gaps":
            good_to_have_gaps
    }