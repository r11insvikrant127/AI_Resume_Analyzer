# resume_rewriter.py

import json
import re


REWRITE_SYSTEM = (
    "You are a professional resume writer. "
    "You NEVER invent experience, employers, dates, "
    "skills, or metrics that are not present in the "
    "source resume. You may only rephrase, restructure, "
    "and emphasize existing information to better match "
    "the job description. Return valid JSON only."
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
            raise ValueError("Rewriter returned invalid JSON.")
        return json.loads(content[start:end + 1])


def rewrite_resume(
    client,
    model,
    resume_text,
    job_description,
):
    """
    Produce three rewrite artifacts:

        tailored_summary     — 3-4 line professional summary
        rewritten_bullets    — list of improved bullet points
        full_rewrite         — full rewritten resume text
        keywords_added       — JD keywords now surfaced
    """

    prompt = f"""
You are rewriting a candidate's resume to better match a
job description.

STRICT RULES:

1. NEVER invent employers, job titles, dates, degrees,
   certifications, projects, technologies, or metrics.

2. You MAY:
   - Rephrase existing bullets with stronger action verbs.
   - Reorder existing content to highlight relevant work.
   - Surface skills/technologies already mentioned in the
     resume but buried in prose.
   - Reuse real numbers that already appear in the resume.
   - Remove filler and redundancy.

3. If the resume has no measurable metrics, do NOT add any.
   Leave the bullet factual.

4. Tailored summary must only use information from the
   resume. It may emphasize JD-relevant strengths but must
   not claim skills the candidate has not demonstrated.

5. Return ONLY valid JSON in this exact structure:

{{
    "tailored_summary": "",
    "rewritten_bullets": [],
    "full_rewrite": "",
    "keywords_added": []
}}

JOB DESCRIPTION:

{job_description}

SOURCE RESUME:

{resume_text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": REWRITE_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    content = response.choices[0].message.content or ""
    data = _parse_json(content)

    return {
        "tailored_summary": str(data.get("tailored_summary", "")).strip(),
        "rewritten_bullets": [
            str(b).strip()
            for b in data.get("rewritten_bullets", [])
            if str(b).strip()
        ],
        "full_rewrite": str(data.get("full_rewrite", "")).strip(),
        "keywords_added": [
            str(k).strip()
            for k in data.get("keywords_added", [])
            if str(k).strip()
        ],
    }


def build_rewrite_pdf_text(rewrite):
    """
    Plain-text version of the rewrite, used by the PDF
    download button in the UI.
    """

    lines = []
    lines.append("TAILORED SUMMARY")
    lines.append(rewrite.get("tailored_summary", ""))
    lines.append("")
    lines.append("REWRITTEN BULLETS")
    for b in rewrite.get("rewritten_bullets", []):
        lines.append(f"• {b}")
    lines.append("")
    lines.append("KEYWORDS SURFACED")
    for k in rewrite.get("keywords_added", []):
        lines.append(f"- {k}")
    lines.append("")
    lines.append("FULL REWRITE")
    lines.append(rewrite.get("full_rewrite", ""))
    return "\n".join(lines)