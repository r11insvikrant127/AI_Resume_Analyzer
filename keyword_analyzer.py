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
# SEMANTIC REQUIREMENT MATCHING
# ============================================================
def compare_requirements_with_resume(
    client,
    model,
    requirements,
    resume_text
):
    """
    Compare JD requirements against explicit evidence in
    the candidate's resume.

    The LLM performs semantic interpretation, but it must
    ground every classification in actual resume evidence.

    No hardcoded skill or technology relationships are used.
    """

    if not requirements:
        return []

    requirement_payload = []

    for requirement in requirements:

        if not isinstance(requirement, dict):
            continue

        name = normalize_skill(
            requirement.get(
                "name",
                ""
            )
        )

        category = get_skill_category(
            requirement
        )

        if not name or category is None:
            continue

        requirement_payload.append({
            "name": name,
            "category": category
        })

    if not requirement_payload:
        return []

    prompt = f"""
You are a strict resume-to-job-requirement matching system.

Your task is to determine whether the candidate's resume
provides evidence for each job requirement.

The most important rule is:

ONLY USE INFORMATION THAT IS ACTUALLY PRESENT IN THE RESUME.

Do not infer, assume, extrapolate, or invent candidate
experience.

------------------------------------------------------------
MATCH STATUS
------------------------------------------------------------

For every requirement return exactly one of:

"matched"

Use matched ONLY when the resume contains explicit evidence
that the candidate has the requirement.

"partial"

Use partial ONLY when the resume contains explicit,
relevant evidence related to the requirement, but that
evidence clearly does not fully satisfy the requirement.

"missing"

Use missing when the resume does not contain explicit
evidence for the requirement.

------------------------------------------------------------
STRICT EVIDENCE RULE
------------------------------------------------------------

The following do NOT count as evidence:

- assumptions
- implications
- inferred experience
- likely knowledge from a degree
- likely knowledge from a job title
- likely knowledge from another technology
- likely knowledge from another course
- generic claims about the candidate
- what a candidate would normally know
- what someone in a particular role would normally use

For example:

If the resume says:

"System administrator"

you MUST NOT conclude:

"Git experience"

unless Git or actual version-control experience is
explicitly mentioned.

If the resume says:

"Python"

you MUST NOT conclude:

"FastAPI"

unless FastAPI or explicit API/framework experience is
actually present.

If the resume says:

"B.Tech in Computer Science"

you MUST NOT automatically conclude that every individual
computer-science topic is satisfied.

------------------------------------------------------------
PARTIAL MATCH RULE
------------------------------------------------------------

Partial does NOT mean:

"the candidate probably knows it."

Partial means:

"The resume explicitly demonstrates something relevant,
but it does not fully demonstrate the requested requirement."

Example:

Requirement:
"REST API development"

Resume:
"Developed HTTP-based backend services"

This may be partial if the evidence is explicit but does
not establish complete REST API experience.

However:

Resume:
"Worked with Java"

Requirement:
"REST API development"

This is missing, NOT partial.

------------------------------------------------------------
MATCH STRENGTH
------------------------------------------------------------

Return:

1.0
Clear and direct evidence.

0.5
Explicit but incomplete evidence.

0.0
No explicit evidence.

Values between these may be used only when the evidence
clearly justifies them.

Do NOT use match_strength to compensate for missing evidence.

------------------------------------------------------------
EVIDENCE
------------------------------------------------------------

For every matched or partial requirement, quote or closely
paraphrase the relevant resume evidence.

The evidence MUST come from the supplied resume.

For missing requirements:

"evidence": ""

Do NOT fabricate evidence.

------------------------------------------------------------
REASON
------------------------------------------------------------

Explain the classification briefly.

The reason must describe the actual relationship between
the resume evidence and the requirement.

Do not use phrases such as:

- "probably"
- "likely"
- "implied"
- "presumably"
- "appears to know"
- "should have"
- "would normally have"

unless those words are directly present in the resume.

------------------------------------------------------------
NO PREDEFINED TECHNOLOGY RELATIONSHIPS
------------------------------------------------------------

Do not use a predefined technology relationship list.

Do not assume that related technologies are equivalent.

Evaluate every requirement independently.

------------------------------------------------------------
REQUIREMENTS
------------------------------------------------------------

{json.dumps(
    requirement_payload,
    indent=2
)}

------------------------------------------------------------
RESUME
------------------------------------------------------------

{resume_text}

------------------------------------------------------------
OUTPUT
------------------------------------------------------------

Return ONLY valid JSON.

Use exactly:

{{
    "matches": [
        {{
            "requirement": "requirement name",
            "category": "technical",
            "status": "matched",
            "match_strength": 1.0,
            "evidence": "Explicit evidence from the resume",
            "reason": "Explanation based only on that evidence"
        }}
    ]
}}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict evidence-based resume "
                    "matching system. Never infer candidate "
                    "experience that is not explicitly supported "
                    "by the resume. Never invent evidence. "
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

    content = (
        response
        .choices[0]
        .message
        .content
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

        data = json.loads(
            content
        )

    except json.JSONDecodeError:

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:

            raise ValueError(
                "Groq did not return valid requirement "
                "matching JSON."
            )

        try:

            data = json.loads(
                content[
                    start:end + 1
                ]
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                "Unable to parse Groq's requirement matching."
            ) from exc

    if not isinstance(data, dict):

        raise ValueError(
            "Groq returned an invalid requirement matching "
            "structure."
        )

    matches = data.get(
        "matches",
        []
    )

    if not isinstance(matches, list):
        matches = []

    # ========================================================
    # VALIDATE RESULTS
    # ========================================================

    valid_statuses = {
        "matched",
        "partial",
        "missing"
    }

    normalized_matches = []

    seen = set()

    for item in matches:

        if not isinstance(item, dict):
            continue

        requirement = normalize_skill(
            item.get(
                "requirement",
                ""
            )
        )

        category = str(
            item.get(
                "category",
                ""
            )
        ).strip().lower()

        status = str(
            item.get(
                "status",
                ""
            )
        ).strip().lower()

        evidence = str(
            item.get(
                "evidence",
                ""
            )
        ).strip()

        reason = str(
            item.get(
                "reason",
                ""
            )
        ).strip()

        if not requirement:
            continue

        if requirement in seen:
            continue

        if category not in ALLOWED_CATEGORIES:
            category = "foundational"

        if status not in valid_statuses:
            status = "missing"

        # ----------------------------------------------------
        # Evidence validation
        # ----------------------------------------------------

        if status in {
            "matched",
            "partial"
        } and not evidence:

            status = "missing"
            reason = (
                "No explicit resume evidence was provided."
            )

        # ----------------------------------------------------
        # Match strength
        # ----------------------------------------------------

        try:

            match_strength = float(
                item.get(
                    "match_strength",
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            match_strength = 0.0

        match_strength = max(
            0.0,
            min(
                1.0,
                match_strength
            )
        )

        # ----------------------------------------------------
        # Keep status and strength consistent
        # ----------------------------------------------------

        if status == "matched":

            match_strength = max(
                match_strength,
                0.75
            )

        elif status == "partial":

            if match_strength <= 0:

                match_strength = 0.5

            match_strength = min(
                match_strength,
                0.74
            )

        elif status == "missing":

            match_strength = 0.0
            evidence = ""

        normalized_matches.append({

            "requirement":
                requirement,

            "category":
                category,

            "status":
                status,

            "match_strength":
                round(
                    match_strength,
                    3
                ),

            "evidence":
                evidence,

            "reason":
                reason
        })

        seen.add(
            requirement
        )

    # ========================================================
    # ENSURE EVERY REQUIREMENT HAS A RESULT
    # ========================================================

    returned_requirements = {
        item["requirement"]
        for item in normalized_matches
    }

    for requirement in requirement_payload:

        name = requirement["name"]

        if name in returned_requirements:
            continue

        normalized_matches.append({

            "requirement":
                name,

            "category":
                requirement["category"],

            "status":
                "missing",

            "match_strength":
                0.0,

            "evidence":
                "",

            "reason":
                "No explicit evidence was found in the resume."
        })

    return normalized_matches


# ============================================================
# ORGANIZE SEMANTIC MATCH RESULTS
# ============================================================

def organize_match_results(
    required_matches,
    good_to_have_matches
):
    """
    Organize semantic requirement matches into the structure
    expected by the rest of the application.
    """

    def classify(matches):

        matched = []
        partial = []
        missing = []

        for item in matches:

            name = item["requirement"]
            status = item["status"]

            if status == "matched":

                matched.append(name)

            elif status == "partial":

                partial.append(name)

            else:

                missing.append(name)

        return (
            matched,
            partial,
            missing
        )

    (
        matched_required,
        partial_required,
        missing_required
    ) = classify(
        required_matches
    )

    (
        matched_good_to_have,
        partial_good_to_have,
        missing_good_to_have
    ) = classify(
        good_to_have_matches
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