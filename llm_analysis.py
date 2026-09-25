# llm_analysis.py

import json
import re


def parse_json_response(content):
    """
    Parse JSON returned by the LLM.

    Also handles responses accidentally wrapped
    in Markdown code fences.
    """

    content = content.strip()

    content = re.sub(r"^```json\s*", "", content, flags=re.IGNORECASE)
    content = re.sub(r"^```\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    try:
        return json.loads(content)

    except json.JSONDecodeError:

        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1:
            try:
                return json.loads(content[start:end + 1])
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "The AI returned an invalid JSON response."
                ) from exc

        raise ValueError(
            "The AI returned an invalid response. "
            "Please try again."
        )


def analyze_resume(client, model, resume_text, job_description):
    """
    Use the LLM for qualitative resume analysis.

    Numerical ATS scoring is NOT performed here.
    """

    prompt = f"""
You are an expert resume analyst.

Analyze the candidate resume against the provided job description.

Your response MUST be valid JSON.

Return exactly this structure:

{{
    "candidate_summary": "",
    "strengths": [],
    "weaknesses": [],
    "experience_match": "",
    "education_match": "",
    "project_match": "",
    "resume_improvements": [],
    "interview_questions": []
}}

Rules:

1. Do not invent candidate experience.

2. Do not assume a skill that is not supported by
   the resume.

3. Base the analysis only on the provided resume
   and job description.

4. interview_questions should contain 10 relevant
   questions.

5. Keep the answer concise but useful.

6. Do not calculate or invent an ATS score.

7. Do not fabricate achievements or metrics.

8. Return JSON only.

RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional resume analyst. "
                    "Return valid JSON only."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content or ""
    return parse_json_response(content)


def generate_resume_tips(client, model, resume_text):
    """
    Generate general resume-improvement suggestions.
    """

    prompt = f"""
Review this resume as a professional resume coach.

Provide 8 practical recommendations to improve it.

Focus on:

- ATS compatibility
- Skills presentation
- Project descriptions
- Achievement statements
- Keywords
- Formatting
- Quantifiable results
- Professional summary

IMPORTANT:

1. Do NOT invent achievements.

2. Do NOT fabricate numbers.

3. Do NOT estimate metrics.

4. Do NOT suggest adding fake percentages,
   fake user counts, fake performance improvements,
   fake revenue, fake rankings, or fake impact.

5. If the resume does not contain measurable results,
   recommend adding real metrics only when the candidate
   can verify them.

6. Recommendations must be based on the actual resume.

Resume:

{resume_text}

Return only a numbered list.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert resume coach. "
                    "Never invent or fabricate candidate "
                    "achievements or metrics."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content or ""