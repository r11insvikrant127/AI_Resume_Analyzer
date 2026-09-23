import re
import json


# ============================================================
# KEYWORD ALIASES
# ============================================================

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
        "problem solving skills"
    ],
    "communication skills": [
        "communication skills",
        "communication"
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
# SKILL TAXONOMY
# ============================================================

SKILL_TAXONOMY = {
    "languages": [
        "java",
        "javascript",
        "typescript",
        "python",
        "sql"
    ],
    "backend_frameworks": [
        "spring boot",
        "fastapi",
        "flask"
    ],
    "frontend_frameworks": [
        "react",
        "next.js",
        "flutter"
    ],
    "databases": [
        "mysql",
        "sqlite",
        "mongodb"
    ],
    "cloud_devops": [
        "docker",
        "aws"
    ],
    "version_control": [
        "git",
        "github"
    ],
    "concepts": [
        "object oriented programming",
        "data structures and algorithms",
        "rest apis",
        "problem solving",
        "communication skills",
        "code reviews",
        "debugging"
    ]
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


# ============================================================
# KEYWORD MATCHING
# ============================================================

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
    matched = []
    missing = []

    for keyword in keywords:
        if keyword_exists(keyword, resume_text):
            matched.append(keyword)
        else:
            missing.append(keyword)

    return matched, missing


# ============================================================
# SKILL TAXONOMY HELPERS
# ============================================================

def get_skill_category(skill):
    normalized = normalize_skill(skill)

    if not normalized:
        return None

    for category, skills in SKILL_TAXONOMY.items():
        if normalized in skills:
            return category

    return None


def resume_has_category(category, resume_text):
    if not category:
        return False

    for skill in SKILL_TAXONOMY.get(category, []):
        if keyword_exists(skill, resume_text):
            return True

    return False


# ============================================================
# DETERMINISTIC SKILL MATCHING
# ============================================================

def _classify_skills(skills, resume_text):
    """
    Classify a list of JD skills against the resume.

    Returns (matched, partial, missing) lists.
    """

    matched = []
    partial = []
    missing = []

    for skill in skills:

        if keyword_exists(skill, resume_text):
            matched.append(skill)
            continue

        category = get_skill_category(skill)

        if resume_has_category(category, resume_text):
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

    Full match    -> skill (or alias) exists in resume
    Partial match -> skill missing, but resume contains
                     another skill from the same category
    Missing       -> skill missing AND no related skill
                     present in resume

    This is the SINGLE SOURCE OF TRUTH for the
    matched / partial / missing classification used
    by the ATS scorer and the skill-gap analyzer.
    """

    (
        matched_required,
        partial_required,
        missing_required
    ) = _classify_skills(required_skills, resume_text)

    (
        matched_good,
        partial_good,
        missing_good
    ) = _classify_skills(good_to_have_skills, resume_text)

    # Combined lists (used for skill-match scoring)
    matched_skills = matched_required + matched_good
    partial_match_skills = partial_required + partial_good
    missing_skills = missing_required + missing_good

    return {
        # Required
        "matched_required": matched_required,
        "partial_required": partial_required,
        "missing_required": missing_required,

        # Good-to-have
        "matched_good_to_have": matched_good,
        "partial_good_to_have": partial_good,
        "missing_good_to_have": missing_good,

        # Combined
        "matched_skills": matched_skills,
        "partial_match_skills": partial_match_skills,
        "missing_skills": missing_skills
    }


# ============================================================
# KEYWORD ANALYSIS
# ============================================================

def calculate_keyword_match(
    required_keywords,
    good_to_have_keywords,
    resume_text
):
    matched_required, missing_required = (
        match_keyword_list(required_keywords, resume_text)
    )

    matched_good, missing_good = (
        match_keyword_list(good_to_have_keywords, resume_text)
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

    total_keywords = (
        len(required_keywords) + len(good_to_have_keywords)
    )
    total_matched = (
        len(matched_required) + len(matched_good)
    )

    if total_keywords:
        overall_percentage = round(
            total_matched / total_keywords * 100
        )
    else:
        overall_percentage = 0

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
# AI KEYWORD EXTRACTION (JD -> required / good-to-have)
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
        cleaned = []
        seen = set()
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