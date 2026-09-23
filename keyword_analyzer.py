import json
import re


# ============================================================
# ALLOWED SKILL CATEGORIES
# ============================================================

ALLOWED_CATEGORIES = {
    "technical",
    "soft_skill",
    "foundational"
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize text for deterministic phrase matching.

    This is generic text processing, not a hardcoded
    skill-specific rule.
    """

    if text is None:
        return ""

    text = str(text).lower()

    text = text.replace("-", " ")
    text = text.replace("_", " ")

    text = re.sub(
        r"[^a-z0-9+#. ]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def normalize_skill(skill):
    """
    Normalize a skill name for comparison and deduplication.
    """

    return normalize_text(skill)


def canonicalize_skill(skill):
    """
    Return a normalized skill name.

    Semantic canonicalization is performed by Groq during
    extraction, rather than through hardcoded Python mappings.
    """

    return normalize_skill(skill)


# ============================================================
# EXACT PHRASE MATCHING
# ============================================================

def phrase_exists(phrase, resume_text):
    """
    Check whether a complete phrase appears in the resume.

    Word boundaries prevent false positives such as:

        Java matching JavaScript
    """

    phrase = normalize_text(phrase)
    resume_text = normalize_text(resume_text)

    if not phrase or not resume_text:
        return False

    pattern = (
        rf"(?<![a-z0-9])"
        rf"{re.escape(phrase)}"
        rf"(?![a-z0-9])"
    )

    return re.search(
        pattern,
        resume_text
    ) is not None


# ============================================================
# SKILL OBJECT HELPERS
# ============================================================

def get_skill_name(skill):
    """
    Accept either:

        "Python"

    or:

        {
            "name": "Python",
            "category": "technical",
            "aliases": [...]
        }
    """

    if isinstance(skill, dict):
        return str(
            skill.get("name", "")
        ).strip()

    if isinstance(skill, str):
        return skill.strip()

    return ""


def get_skill_category(skill):
    """
    Read the category supplied by Groq.

    Unknown categories are not silently classified as
    technical.
    """

    if not isinstance(skill, dict):
        return None

    category = str(
        skill.get("category", "")
    ).strip().lower()

    if category in ALLOWED_CATEGORIES:
        return category

    return None


def get_skill_aliases(skill):
    """
    Return the skill's canonical name and supplied aliases.

    Aliases come from the extracted skill object, not from
    a global hardcoded dictionary.
    """

    name = get_skill_name(skill)

    if not name:
        return []

    aliases = [name]

    if isinstance(skill, dict):

        supplied_aliases = skill.get(
            "aliases",
            []
        )

        if isinstance(supplied_aliases, list):

            for alias in supplied_aliases:

                if isinstance(alias, str):
                    aliases.append(alias)

    cleaned = []
    seen = set()

    for alias in aliases:

        normalized = normalize_skill(alias)

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)
        cleaned.append(normalized)

    return cleaned


def clean_skill_objects(skills):
    """
    Validate, normalize, and deduplicate Groq's skill objects.

    Every retained skill must have:

        name
        category
        aliases
    """

    if not isinstance(skills, list):
        return []

    cleaned = []
    seen = set()

    for skill in skills:

        if not isinstance(skill, dict):
            continue

        name = normalize_skill(
            skill.get("name", "")
        )

        category = get_skill_category(skill)

        if not name or category is None:
            continue

        if name in seen:
            continue

        aliases = get_skill_aliases(skill)

        cleaned.append({
            "name": name,
            "category": category,
            "aliases": aliases
        })

        seen.add(name)

    return cleaned


# ============================================================
# KEYWORD MATCHING
# ============================================================

def keyword_exists(keyword, resume_text):
    """
    Check for explicit evidence of a skill in the resume.

    Supports both a plain string and a structured skill.

    A skill is matched when its name or one of its supplied
    aliases explicitly appears in the resume.
    """

    aliases = get_skill_aliases(keyword)

    for alias in aliases:

        if phrase_exists(
            alias,
            resume_text
        ):
            return True

    return False


def match_keyword_list(keywords, resume_text):
    """
    Deterministically match a list of skills.

    Returns:
        matched
        missing

    Results contain normalized skill names for compatibility
    with the existing app.
    """

    matched = []
    missing = []

    seen = set()

    for skill in keywords:

        name = normalize_skill(
            get_skill_name(skill)
        )

        if not name or name in seen:
            continue

        seen.add(name)

        if keyword_exists(
            skill,
            resume_text
        ):

            matched.append(name)

        else:

            missing.append(name)

    return matched, missing


# ============================================================
# TECHNICAL / NON-TECHNICAL CLASSIFICATION
# ============================================================

def is_technical_skill(skill):
    """
    Determine whether a structured skill is technical.

    This function requires Groq's category information.
    It does not guess from the skill's name.
    """

    category = get_skill_category(skill)

    if category is None:

        raise ValueError(
            "Skill category is missing. Pass a structured "
            "skill object containing 'name' and 'category'."
        )

    return category == "technical"


def split_technical_skills(skills):
    """
    Split structured skills into:

        technical
        non_technical

    Returns normalized skill names.

    IMPORTANT:
    Pass the structured skill objects returned by
    extract_keywords_from_jd(), not the legacy string lists.
    """

    technical = []
    non_technical = []

    seen = set()

    for skill in skills:

        name = normalize_skill(
            get_skill_name(skill)
        )

        if not name or name in seen:
            continue

        seen.add(name)

        if is_technical_skill(skill):

            technical.append(name)

        else:

            non_technical.append(name)

    return technical, non_technical


# ============================================================
# DETERMINISTIC SKILL CLASSIFICATION
# ============================================================

def _classify(skill, resume_text):
    """
    Classify a skill based on explicit resume evidence.

    This version does not invent partial relationships
    between technologies.

    A semantic partial-match stage can be added separately
    with evidence from the actual resume.
    """

    if keyword_exists(
        skill,
        resume_text
    ):
        return "matched"

    return "missing"


def _classify_list(skills, resume_text):
    """
    Classify an entire list of skills.

    The partial list is retained for compatibility with
    the existing app and scorer.
    """

    matched = []
    partial = []
    missing = []

    seen = set()

    for skill in skills:

        name = normalize_skill(
            get_skill_name(skill)
        )

        if not name or name in seen:
            continue

        seen.add(name)

        verdict = _classify(
            skill,
            resume_text
        )

        if verdict == "matched":

            matched.append(name)

        elif verdict == "partial":

            partial.append(name)

        else:

            missing.append(name)

    return matched, partial, missing


def match_deterministic_skills(
    required_skills,
    good_to_have_skills,
    resume_text
):
    """
    Match required and good-to-have skills separately.

    Accepts structured skill objects so that Groq-supplied
    aliases can be used during deterministic matching.
    """

    (
        matched_required,
        partial_required,
        missing_required
    ) = _classify_list(
        required_skills,
        resume_text
    )

    (
        matched_good_to_have,
        partial_good_to_have,
        missing_good_to_have
    ) = _classify_list(
        good_to_have_skills,
        resume_text
    )

    return {

        "matched_required":
            matched_required,

        "partial_required":
            partial_required,

        "missing_required":
            missing_required,

        "matched_good_to_have":
            matched_good_to_have,

        "partial_good_to_have":
            partial_good_to_have,

        "missing_good_to_have":
            missing_good_to_have,

        # Existing app compatibility

        "matched_skills":
            matched_required
            + matched_good_to_have,

        "partial_match_skills":
            partial_required
            + partial_good_to_have,

        "missing_skills":
            missing_required
            + missing_good_to_have
    }


# ============================================================
# KEYWORD MATCH PERCENTAGES
# ============================================================

def calculate_keyword_match(
    required_keywords,
    good_to_have_keywords,
    resume_text
):
    """
    Calculate deterministic keyword match percentages.

    Required Keyword Match:
        matched required / total required

    Good-to-Have Match:
        matched optional / total optional

    Overall Keyword Match:
        total matched / total extracted skills
    """

    (
        matched_required,
        missing_required
    ) = match_keyword_list(
        required_keywords,
        resume_text
    )

    (
        matched_good_to_have,
        missing_good_to_have
    ) = match_keyword_list(
        good_to_have_keywords,
        resume_text
    )

    total_required = (
        len(matched_required)
        + len(missing_required)
    )

    total_good_to_have = (
        len(matched_good_to_have)
        + len(missing_good_to_have)
    )

    total_keywords = (
        total_required
        + total_good_to_have
    )

    total_matched = (
        len(matched_required)
        + len(matched_good_to_have)
    )

    required_percentage = (
        round(
            len(matched_required)
            / total_required
            * 100
        )
        if total_required
        else 0
    )

    good_to_have_percentage = (
        round(
            len(matched_good_to_have)
            / total_good_to_have
            * 100
        )
        if total_good_to_have
        else 0
    )

    overall_percentage = (
        round(
            total_matched
            / total_keywords
            * 100
        )
        if total_keywords
        else 0
    )

    return {

        "matched_required":
            matched_required,

        "missing_required":
            missing_required,

        "matched_good_to_have":
            matched_good_to_have,

        "missing_good_to_have":
            missing_good_to_have,

        "required_percentage":
            required_percentage,

        "good_to_have_percentage":
            good_to_have_percentage,

        "overall_percentage":
            overall_percentage
    }


# ============================================================
# AI KEYWORD EXTRACTION
# ============================================================

def extract_keywords_from_jd(
    client,
    model,
    job_description
):
    """
    Use Groq to:

    1. Extract JD skills.
    2. Identify required vs good-to-have.
    3. Normalize equivalent wording.
    4. Categorize each skill.
    5. Supply safe, equivalent aliases.

    Python validates the structure and handles subsequent
    deterministic matching and scoring.
    """

    prompt = f"""
You are a job-description skill extraction system.

Analyze the job description provided below.

Extract the skills and requirements that are actually
mentioned in the job description.

Return two groups:

1. required_skills
2. good_to_have_skills

For EVERY skill, return:

- name
- category
- aliases

------------------------------------------------------------
SKILL NAME
------------------------------------------------------------

The name must be a concise, normalized skill concept.

Remove descriptive adjectives that do not change the
underlying skill.

For example, different descriptions of communication
ability should be represented by the underlying
communication skill concept.

Do not split a single established skill concept into
unrelated fragments.

Do not merge distinct technologies or unrelated skills.

Preserve important technical distinctions.

For example:

Java is not JavaScript.
SQL is not MySQL.
React is not Angular.

------------------------------------------------------------
CATEGORIES
------------------------------------------------------------

Use exactly ONE of these categories for each skill:

technical
soft_skill
foundational

technical:
Specific programming languages, frameworks, libraries,
databases, tools, APIs, platforms, development technologies,
technical practices, and identifiable technical skills.

soft_skill:
Communication, collaboration, teamwork, leadership,
problem solving, adaptability, interpersonal abilities,
and similar behavioral skills.

foundational:
Broad underlying knowledge requirements, general
programming foundations, computer science fundamentals,
and general conceptual foundations.

Classify based on the actual meaning of the requirement,
not merely on whether its wording contains the word
"programming" or "technical".

------------------------------------------------------------
ALIASES
------------------------------------------------------------

Provide a short list of genuinely equivalent expressions
for the SAME skill.

Aliases may include standard abbreviations, expanded
forms, and equivalent naming conventions.

Do not include:

- Different technologies
- Merely related technologies
- Broader or narrower skills that are not equivalent
- Speculative experience
- Entire sentences

An alias must be safe to count as explicit evidence of
the same skill in a resume.

If no safe alias exists, return an empty list.

------------------------------------------------------------
REQUIRED VS GOOD-TO-HAVE
------------------------------------------------------------

Use the JD's wording to determine whether a skill is
required or optional.

Do not place the same normalized skill in both groups.

If the JD clearly treats a skill as required, required
takes priority.

Do not invent requirements.

------------------------------------------------------------
OUTPUT
------------------------------------------------------------

Return ONLY valid JSON in this structure:

{{
    "required_skills": [
        {{
            "name": "Python",
            "category": "technical",
            "aliases": []
        }},
        {{
            "name": "Communication",
            "category": "soft_skill",
            "aliases": []
        }}
    ],
    "good_to_have_skills": [
        {{
            "name": "Spring Boot",
            "category": "technical",
            "aliases": []
        }}
    ]
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
                    "You extract and normalize job-description "
                    "skills. Return valid JSON only. Do not "
                    "invent requirements or treat related "
                    "technologies as equivalent."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = (
        response
        .choices[0]
        .message.content
        or ""
    ).strip()

    # ========================================================
    # REMOVE OPTIONAL MARKDOWN FENCES
    # ========================================================

    content = re.sub(
        r"^```(?:json)?\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = re.sub(
        r"\s*```$",
        "",
        content
    )

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        data = json.loads(content)

    except json.JSONDecodeError:

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:

            raise ValueError(
                "Groq did not return valid skill extraction JSON."
            )

        try:

            data = json.loads(
                content[start:end + 1]
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                "Unable to parse Groq's skill extraction."
            ) from exc

    if not isinstance(data, dict):

        raise ValueError(
            "Groq returned an invalid skill extraction structure."
        )

    # ========================================================
    # VALIDATE SKILLS
    # ========================================================

    required_skills = clean_skill_objects(
        data.get(
            "required_skills",
            []
        )
    )

    good_to_have_skills = clean_skill_objects(
        data.get(
            "good_to_have_skills",
            []
        )
    )

    # ========================================================
    # REMOVE CROSS-CATEGORY DUPLICATES
    # ========================================================

    required_names = {
        skill["name"]
        for skill in required_skills
    }

    good_to_have_skills = [
        skill
        for skill in good_to_have_skills
        if skill["name"] not in required_names
    ]

    # ========================================================
    # LEGACY NAME LISTS
    # ========================================================
    #
    # These keep the old app's keyword display compatible.
    #
    # The updated app must use required_skills and
    # good_to_have_skills for category-aware scoring.
    # ========================================================

    required_keywords = [
        skill["name"]
        for skill in required_skills
    ]

    good_to_have_keywords = [
        skill["name"]
        for skill in good_to_have_skills
    ]

    # ========================================================
    # RETURN STRUCTURED AND LEGACY DATA
    # ========================================================

    return {

        "required_skills":
            required_skills,

        "good_to_have_skills":
            good_to_have_skills,

        "required_keywords":
            required_keywords,

        "good_to_have_keywords":
            good_to_have_keywords
    }