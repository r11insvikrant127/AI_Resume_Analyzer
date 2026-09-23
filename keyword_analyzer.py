import re
import json


# ============================================================
# KEYWORD ALIASES
# ============================================================
# Aliases define what counts as EXACT presence of a skill.
# Keep these conservative — overly broad aliases cause
# false-positive matches in an ATS context.

KEYWORD_ALIASES = {
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "python": ["python"],
    "sql": ["sql"],
    "mysql": ["mysql"],
    "object oriented programming": [
        "object oriented programming",
        "object-oriented programming",
        "oop"
    ],
    "data structures and algorithms": [
        "data structures and algorithms",
        "data structures & algorithms",
        "dsa"
    ],
    "rest apis": [
        "rest api",
        "rest apis",
        "restful api",
        "restful apis"
    ],
    "problem solving": [
        "problem solving",
        "problem-solving",
        "problem solving skills",
        "analytical skills",
        "analytical thinking"
    ],
    # NOTE: "communication" alone is too broad
    # (e.g. "communication between client and server").
    "communication skills": [
        "communication skills",
        "verbal communication",
        "written communication",
        "interpersonal skills"
    ],
    "code reviews": ["code review", "code reviews"],
    "debugging": ["debugging", "debug", "debugged"],
    "spring boot": ["spring boot"],
    "fastapi": ["fastapi", "fast api"],
    "docker": ["docker"],
    "aws": ["aws", "amazon web services"],
    "git": ["git"],
    "github": ["github"],
    "mongodb": ["mongodb", "mongo db"],
    "sqlite": ["sqlite"],
    "flask": ["flask"],
    "flutter": ["flutter"],
    "react": ["react", "reactjs", "react.js"],
    "next.js": ["next.js", "nextjs", "next js"]
}


# ============================================================
# TECHNICAL vs. NON-TECHNICAL
# ============================================================
# Skills listed here are treated as non-technical for the
# purpose of the "Technical Skill Match" component of the
# ATS score. They still count toward "Required Keyword Match".

NON_TECHNICAL_SKILLS = {
    "communication skills",
    "problem solving"
}


def is_technical_skill(skill):
    return normalize_skill(skill) not in NON_TECHNICAL_SKILLS


# ============================================================
# SKILL RELATIONS (explicit "partial" links)
# ============================================================
# If the JD requires skill X and the resume contains Y,
# and Y is listed as a relation of X, then X is a PARTIAL
# match. Otherwise, X is MISSING.
#
# Keep this list narrow and defensible.

SKILL_RELATIONS = {
    # Backend frameworks
    "spring boot": ["fastapi", "flask"],
    "fastapi": ["flask", "spring boot"],
    "flask": ["fastapi", "spring boot"],

    # Frontend
    "react": ["next.js"],
    "next.js": ["react"],
    "flutter": [],

    # Databases
    "mysql": ["sqlite", "mongodb"],
    "sqlite": ["mysql"],
    "mongodb": ["mysql", "sqlite"],

    # Languages — deliberately narrow
    # Java <-> JavaScript is NOT a relation.
    # Java <-> Python is NOT a relation.
    "javascript": ["typescript"],
    "typescript": ["javascript"],
    "java": [],
    "python": [],

    # Cloud / DevOps
    "docker": [],
    "aws": [],

    # Version control
    "git": ["github"],
    "github": ["git"],

    # Technical concepts
    "rest apis": [],
    "object oriented programming": [],
    "data structures and algorithms": [],
    "debugging": ["code reviews"],
    "code reviews": ["debugging"]
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    text = text.lower()
    text = text.replace("-", " ")
    text = text.replace("_", " ")
    text = re.sub(r"[^a-z0-9+#. ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_skill(skill):
    if not skill:
        return ""
    skill = skill.lower().strip()
    if "(" in skill:
        skill = skill.split("(")[0]
    return " ".join(skill.split())


# ============================================================
# EXACT WORD / PHRASE MATCHING
# ============================================================

def phrase_exists(phrase, resume_text):
    phrase = normalize_text(phrase)
    resume_text = normalize_text(resume_text)

    if not phrase:
        return False

    pattern = (
        rf"(?<![a-z0-9])"
        rf"{re.escape(phrase)}"
        rf"(?![a-z0-9])"
    )

    return re.search(pattern, resume_text) is not None


def keyword_exists(keyword, resume_text):
    keyword_normalized = normalize_text(keyword)

    aliases = KEYWORD_ALIASES.get(
        keyword_normalized,
        [keyword]
    )

    for alias in aliases:
        if phrase_exists(alias, resume_text):
            return True

    return False


def match_keyword_list(keywords, resume_text):
    matched, missing = [], []

    for keyword in keywords:
        if keyword_exists(keyword, resume_text):
            matched.append(keyword)
        else:
            missing.append(keyword)

    return matched, missing


# ============================================================
# EXPLICIT PARTIAL-MATCH LOOKUP
# ============================================================

def _has_explicit_relation(skill, resume_text):
    """
    Return True if the resume contains a skill that is
    explicitly listed as a relation of `skill`.
    """

    normalized = normalize_skill(skill)

    for related in SKILL_RELATIONS.get(normalized, []):
        if keyword_exists(related, resume_text):
            return True

    return False


# ============================================================
# DETERMINISTIC CLASSIFICATION
# ============================================================

def _classify(skill, resume_text):
    """
    Classify a single skill as 'matched', 'partial', or 'missing'.
    """

    if keyword_exists(skill, resume_text):
        return "matched"

    if _has_explicit_relation(skill, resume_text):
        return "partial"

    return "missing"


def _classify_list(skills, resume_text):
    matched, partial, missing = [], [], []

    for skill in skills:
        verdict = _classify(skill, resume_text)

        if verdict == "matched":
            matched.append(skill)
        elif verdict == "partial":
            partial.append(skill)
        else:
            missing.append(skill)

    return matched, partial, missing


def match_deterministic_skills(
    required_skills,
    good_to_have_skills,
    resume_text
):
    """
    Deterministic classification of JD skills.

    Matched  -> skill (or alias) present in resume
    Partial  -> skill missing, but an EXPLICITLY RELATED skill
                is present in the resume
    Missing  -> neither the skill nor any related skill present

    This is the SINGLE SOURCE OF TRUTH for ATS scoring and
    for the skill-gap analysis.
    """

    matched_r, partial_r, missing_r = _classify_list(
        required_skills, resume_text
    )

    matched_g, partial_g, missing_g = _classify_list(
        good_to_have_skills, resume_text
    )

    return {
        "matched_required": matched_r,
        "partial_required": partial_r,
        "missing_required": missing_r,

        "matched_good_to_have": matched_g,
        "partial_good_to_have": partial_g,
        "missing_good_to_have": missing_g,

        # Combined (used by skill-gap display)
        "matched_skills": matched_r + matched_g,
        "partial_match_skills": partial_r + partial_g,
        "missing_skills": missing_r + missing_g
    }


# ============================================================
# TECHNICAL-SKILL FILTER
# ============================================================

def split_technical_skills(skills):
    """
    Split a list of skills into (technical, non_technical).
    Used to compute the Technical Skill Match component.
    """

    technical, non_technical = [], []

    for skill in skills:
        if is_technical_skill(skill):
            technical.append(skill)
        else:
            non_technical.append(skill)

    return technical, non_technical


# ============================================================
# KEYWORD ANALYSIS (for display)
# ============================================================

def calculate_keyword_match(
    required_keywords,
    good_to_have_keywords,
    resume_text
):
    matched_required, missing_required = match_keyword_list(
        required_keywords, resume_text
    )
    matched_good, missing_good = match_keyword_list(
        good_to_have_keywords, resume_text
    )

    if required_keywords:
        required_percentage = round(
            len(matched_required) / len(required_keywords) * 100
        )
    else:
        required_percentage = 0

    if good_to_have_keywords:
        good_to_have_percentage = round(
            len(matched_good) / len(good_to_have_keywords) * 100
        )
    else:
        good_to_have_percentage = 0

    total = len(required_keywords) + len(good_to_have_keywords)
    total_matched = len(matched_required) + len(matched_good)

    overall_percentage = (
        round(total_matched / total * 100) if total else 0
    )

    return {
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_good_to_have": matched_good,
        "missing_good_to_have": missing_good,
        "required_percentage": required_percentage,
        "good_to_have_percentage": good_to_have_percentage,
        "overall_percentage": overall_percentage
    }


# ============================================================
# AI KEYWORD EXTRACTION
# ============================================================

def extract_keywords_from_jd(client, model, job_description):
    prompt = f"""
You are an ATS keyword extraction system.

Analyze the following job description.

Separate the important technical/job-related keywords
into two categories:

1. required_keywords
2. good_to_have_keywords

Use the job description itself to determine the category.

Include:

- Programming languages
- Frameworks
- Libraries
- Databases
- Tools
- Technologies
- Technical concepts
- Important job-related skills

Do NOT include:

- Generic words such as "job", "candidate", "company"
- Articles such as "the", "a", "an"
- Entire sentences
- Very common verbs such as "work", "use", "develop"

Keep the technical names as they appear in the job description.

Return ONLY valid JSON in exactly this format:

{{
    "required_keywords": ["Python", "Java", "SQL"],
    "good_to_have_keywords": ["Spring Boot", "Docker", "AWS"]
}}

JOB DESCRIPTION:

{job_description}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an ATS keyword extraction system. "
                    "Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    content = re.sub(r"^```json\s*", "", content, flags=re.IGNORECASE)
    content = re.sub(r"^```\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(
                "Unable to extract keywords from the job description."
            )
        data = json.loads(content[start:end + 1])

    required_keywords = data.get("required_keywords", [])
    good_to_have_keywords = data.get("good_to_have_keywords", [])

    if not isinstance(required_keywords, list):
        required_keywords = []

    if not isinstance(good_to_have_keywords, list):
        good_to_have_keywords = []

    def clean_keywords(keywords):
        cleaned, seen = [], set()
        for keyword in keywords:
            if not isinstance(keyword, str):
                continue
            keyword = keyword.strip()
            if not keyword:
                continue
            normalized = keyword.lower()
            if normalized not in seen:
                cleaned.append(keyword)
                seen.add(normalized)
        return cleaned

    return {
        "required_keywords": clean_keywords(required_keywords),
        "good_to_have_keywords": clean_keywords(good_to_have_keywords)
    }