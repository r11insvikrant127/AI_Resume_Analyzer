
# candidate_ranker.py

DEFAULT_WEIGHTS = {
    "ats_score": 0.35,
    "required_match_percentage": 0.25,
    "technical_skill_percentage": 0.25,
    "good_to_have_match_percentage": 0.05,
    "keyword_coverage": 0.10,
}


def _safe(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def compute_composite_score(result, weights=None):
    weights = weights or DEFAULT_WEIGHTS

    ats_kw = result.get("ats_keyword_analysis", {}) or {}
    keyword_cov = ats_kw.get("required_coverage", 0)

    signal_values = {
        "ats_score": _safe(result.get("ats_score")),
        "required_match_percentage": _safe(result.get("required_match_percentage")),
        "technical_skill_percentage": _safe(result.get("technical_skill_percentage")),
        "good_to_have_match_percentage": _safe(result.get("good_to_have_match_percentage")),
        "keyword_coverage": _safe(keyword_cov),
    }

    total_weight = sum(weights.values()) or 1.0
    composite = sum(
        signal_values[k] * weights.get(k, 0)
        for k in signal_values
    ) / total_weight

    return round(composite, 2), signal_values


def rank_candidates(results, weights=None):
    """
    Return results sorted by composite score, each entry
    enriched with 'composite_score' and 'signal_values'.
    """

    enriched = []

    for r in results:
        score, signals = compute_composite_score(r, weights)
        enriched.append({
            **r,
            "composite_score": score,
            "signal_values": signals,
        })

    enriched.sort(
        key=lambda x: x["composite_score"],
        reverse=True,
    )

    for i, r in enumerate(enriched, start=1):
        r["rank"] = i

    return enriched