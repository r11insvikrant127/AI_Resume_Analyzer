# job_recommender.py

import json
import re


SYSTEM = (
    "You are a career advisor. Recommend job roles that "
    "genuinely fit the candidate's demonstrated skills. "
    "Never invent experience. Return valid JSON only."
)


def _parse_json(content):
    content = content.strip()
    content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\s*```$", "", content)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Recommender returned invalid JSON.")
        return json.loads(content[start:end + 1])


def recommend_jobs(
    client,
    model,
    resume_text,
    matched_skills,
    missing_skills,
    ats_score,
):
    """
    Return:

        roles              — list of {title, fit, reason, level}
        search_terms       — list of boolean search strings
        adjacent_roles     — roles the candidate could grow into
    """

    prompt = f"""
You are a career advisor.

Based ONLY on the candidate's demonstrated skills and the
matched/missing skill lists below, recommend suitable roles.

RULES:

1. Do NOT recommend roles that require skills the candidate
   has not demonstrated.

2. Fit score is 0-100 based on evidence, not aspiration.

3. Provide 3-6 roles total.

4. Provide 4-6 job-board search strings (boolean syntax OK).

5. Provide 2-4 adjacent roles the candidate could grow into
   with upskilling, and note the gap.

6. Return ONLY valid JSON:

{{
    "roles": [
        {{
            "title": "Backend Engineer",
            "level": "mid",
            "fit": 87,
            "reason": "Strong Python + REST + SQL evidence."
        }}
    ],
    "search_terms": [
        "\\"Python\\" AND (\\"FastAPI\\" OR \\"Django\\")"
    ],
    "adjacent_roles": [
        {{
            "title": "Data Engineer",
            "gap": "Needs Airflow / Spark exposure."
        }}
    ]
}}

MATCHED SKILLS:

{json.dumps(matched_skills, indent=2)}

MISSING SKILLS:

{json.dumps(missing_skills, indent=2)}

ATS SCORE: {ats_score}%

RESUME:

{resume_text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content or ""
    data = _parse_json(content)

    roles = []
    for r in data.get("roles", []):
        if not isinstance(r, dict):
            continue
        roles.append({
            "title": str(r.get("title", "")).strip(),
            "level": str(r.get("level", "")).strip(),
            "fit": int(r.get("fit", 0) or 0),
            "reason": str(r.get("reason", "")).strip(),
        })

    roles.sort(key=lambda r: r["fit"], reverse=True)

    return {
        "roles": roles,
        "search_terms": [
            str(s).strip()
            for s in data.get("search_terms", [])
            if str(s).strip()
        ],
        "adjacent_roles": [
            {
                "title": str(a.get("title", "")).strip(),
                "gap": str(a.get("gap", "")).strip(),
            }
            for a in data.get("adjacent_roles", [])
            if isinstance(a, dict)
        ],
    }