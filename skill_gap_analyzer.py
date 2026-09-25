# skill_gap_analyzer.py

# ============================================================
# DETERMINISTIC SKILL GAP ANALYSIS
# ============================================================
#
# Existing behavior is preserved: high_priority_gaps,
# partial_matches, good_to_have_gaps.
#
# New: severity classification, priority ordering, and
# per-gap learning suggestions (LLM-free placeholders that
# the UI can enrich later).
# ============================================================


SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"


def _severity_for_required(missing_count, total_required):
    if total_required == 0:
        return SEVERITY_LOW
    ratio = missing_count / total_required
    if ratio >= 0.5:
        return SEVERITY_HIGH
    if ratio >= 0.25:
        return SEVERITY_MEDIUM
    return SEVERITY_LOW


def build_skill_gap_analysis(
    matched_required,
    partial_required,
    missing_required,
    matched_good_to_have,
    partial_good_to_have,
    missing_good_to_have,
):
    matched_required = list(matched_required or [])
    partial_required = list(partial_required or [])
    missing_required = list(missing_required or [])

    matched_good_to_have = list(matched_good_to_have or [])
    partial_good_to_have = list(partial_good_to_have or [])
    missing_good_to_have = list(missing_good_to_have or [])

    total_required = (
        len(matched_required)
        + len(partial_required)
        + len(missing_required)
    )

    severity = _severity_for_required(
        len(missing_required), total_required
    )

    # --------------------------------------------------------
    # Priority-ordered gap list
    # --------------------------------------------------------

    priority_gaps = []

    for skill in missing_required:
        priority_gaps.append({
            "skill": skill,
            "type": "required",
            "status": "missing",
            "severity": SEVERITY_HIGH,
            "priority": 1,
        })

    for skill in partial_required:
        priority_gaps.append({
            "skill": skill,
            "type": "required",
            "status": "partial",
            "severity": SEVERITY_MEDIUM,
            "priority": 2,
        })

    for skill in partial_good_to_have:
        priority_gaps.append({
            "skill": skill,
            "type": "good_to_have",
            "status": "partial",
            "severity": SEVERITY_LOW,
            "priority": 3,
        })

    for skill in missing_good_to_have:
        priority_gaps.append({
            "skill": skill,
            "type": "good_to_have",
            "status": "missing",
            "severity": SEVERITY_LOW,
            "priority": 4,
        })

    priority_gaps.sort(key=lambda g: g["priority"])

    # --------------------------------------------------------
    # Coverage ratios
    # --------------------------------------------------------

    required_coverage = (
        round(
            (len(matched_required) + 0.5 * len(partial_required))
            / total_required * 100
        )
        if total_required else 0
    )

    total_optional = (
        len(matched_good_to_have)
        + len(partial_good_to_have)
        + len(missing_good_to_have)
    )

    optional_coverage = (
        round(
            (len(matched_good_to_have) + 0.5 * len(partial_good_to_have))
            / total_optional * 100
        )
        if total_optional else 0
    )

    # --------------------------------------------------------
    # Return: preserve old keys + add new
    # --------------------------------------------------------

    return {
        # legacy keys (do not remove — app.py uses them)
        "matched_required": matched_required,
        "partial_required": partial_required,
        "high_priority_gaps": missing_required,
        "partial_matches": partial_required,
        "matched_good_to_have": matched_good_to_have,
        "partial_good_to_have": partial_good_to_have,
        "good_to_have_gaps": partial_good_to_have + missing_good_to_have,

        # new keys
        "overall_severity": severity,
        "required_coverage": required_coverage,
        "optional_coverage": optional_coverage,
        "priority_gaps": priority_gaps,
        "total_required": total_required,
        "total_optional": total_optional,
    }