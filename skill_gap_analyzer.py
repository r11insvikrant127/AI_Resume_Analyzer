# ============================================================
# SKILL GAP ANALYZER
# ============================================================
#
# This module is a PURE PRESENTER of the deterministic
# classification produced by
# keyword_analyzer.match_deterministic_skills().
#
# It does NOT consult the LLM.
#
# Priority rules (deterministic):
#
#   Required skill:
#       matched  -> not a gap
#       partial  -> "Partial / Needs More Evidence"
#       missing  -> "High Priority"
#
#   Good-to-have skill:
#       matched  -> not a gap
#       partial  -> "Partial / Needs More Evidence"
#       missing  -> "Good-to-Have Gap"
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
    Build display buckets from deterministic
    classification.

    All arguments are lists of skill names produced by
    keyword_analyzer.match_deterministic_skills().
    """

    high_priority = list(missing_required or [])

    partial = (
        list(partial_required or [])
        + list(partial_good_to_have or [])
    )

    good_to_have_gaps = list(missing_good_to_have or [])

    return {
        "matched_required":
            list(matched_required or []),

        "partial_required":
            list(partial_required or []),

        "high_priority_gaps":
            high_priority,

        "partial_matches":
            partial,

        "matched_good_to_have":
            list(matched_good_to_have or []),

        "partial_good_to_have":
            list(partial_good_to_have or []),

        "good_to_have_gaps":
            good_to_have_gaps
    }