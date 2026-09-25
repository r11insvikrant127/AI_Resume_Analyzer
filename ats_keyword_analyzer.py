# ats_keyword_analyzer.py

import re


def _normalize(text):
    if not text:
        return ""
    text = text.lower().replace("-", " ").replace("_", " ")
    text = re.sub(r"[^a-z0-9+#. ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _word_count(text):
    return len(_normalize(text).split())


def _count_occurrences(keyword, text):
    kw = _normalize(keyword)
    if not kw:
        return 0
    pattern = rf"(?<![a-z0-9]){re.escape(kw)}(?![a-z0-9])"
    return len(re.findall(pattern, _normalize(text)))


def _find_section(text, section_keywords, max_chars=400):
    """
    Very lightweight section detector. Returns a snippet
    around the first match of any section keyword, or "".
    """
    t = _normalize(text)
    for kw in section_keywords:
        idx = t.find(_normalize(kw))
        if idx != -1:
            return t[idx: idx + max_chars]
    return ""


def analyze_ats_keywords(resume_text, required_skills, good_to_have_skills):
    """
    Compute ATS-oriented keyword stats:

      - density of each required / good-to-have keyword
      - placement in the top of the resume
      - presence in the skills section (if detectable)
      - total keyword coverage
      - mechanical checks (length, contact, sections)
    """

    total_words = _word_count(resume_text) or 1
    resume_lower = _normalize(resume_text)

    top_region = resume_lower[: int(len(resume_lower) * 0.25)]
    skills_region = _find_section(
        resume_text,
        ["skills", "technical skills", "core competencies"],
    )

    keyword_rows = []
    seen = set()

    all_skills = [
        (s, "required") for s in (required_skills or [])
    ] + [
        (s, "good_to_have") for s in (good_to_have_skills or [])
    ]

    for skill, tier in all_skills:

        name = skill.get("name") if isinstance(skill, dict) else str(skill)
        name = (name or "").strip()

        if not name:
            continue

        key = name.lower()

        if key in seen:
            continue

        seen.add(key)

        count = _count_occurrences(name, resume_text)
        density = round(count / total_words * 1000, 2)  # per 1000 words

        keyword_rows.append({
            "keyword": name,
            "tier": tier,
            "count": count,
            "density_per_1000": density,
            "in_top_quarter": _count_occurrences(name, top_region) > 0,
            "in_skills_section": (
                _count_occurrences(name, skills_region) > 0
                if skills_region else False
            ),
        })

    required_rows = [r for r in keyword_rows if r["tier"] == "required"]

    present_required = [r for r in required_rows if r["count"] > 0]

    required_coverage = (
        round(len(present_required) / len(required_rows) * 100)
        if required_rows else 0
    )

    # --------------------------------------------------------
    # Mechanical checks
    # --------------------------------------------------------

    has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", resume_text))
    has_phone = bool(re.search(r"(\+?\d[\d\s\-().]{7,}\d)", resume_text))
    has_skills_header = bool(skills_region)

    checks = {
        "word_count": total_words,
        "word_count_ok": 250 <= total_words <= 1100,
        "has_email": has_email,
        "has_phone": has_phone,
        "has_skills_section": has_skills_header,
    }

    return {
        "total_words": total_words,
        "required_coverage": required_coverage,
        "keyword_rows": keyword_rows,
        "checks": checks,
    }