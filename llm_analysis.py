# llm_analysis.py

import json
import re

from groq_helper import safe_chat


def parse_json_response(content):
    """
    Parse JSON returned by the LLM.

    Also handles responses accidentally wrapped
    in Markdown code fences.
    """

    content = content.strip()

    content = re.sub(
        r"^```json\s*",
        "",
        content,
        flags=re.IGNORECASE,
    )
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

    Interview questions are generated dynamically from the
    supplied resume and job description. No resume-specific
    questions are hardcoded.
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

2. Do not assume a skill that is not explicitly supported
   by the resume.

3. Base candidate-specific claims only on information
   explicitly present in the provided resume.

4. The job description describes the target role and its
   requirements. Do NOT treat technologies, responsibilities,
   qualifications, or skills mentioned only in the job
   description as evidence that the candidate possesses them.

5. interview_questions must contain exactly 10 relevant
   questions.

6. Generate the interview questions dynamically from the
   candidate's actual resume and the job description.

7. Questions should preferably explore information explicitly
   present in the candidate's:
   - projects
   - work experience
   - technical skills
   - education
   - achievements
   - responsibilities

8. Do not use a fixed or reusable question list. The questions
   should change according to the contents of each resume.

9. Do not create a question that assumes the candidate used
   a specific algorithm, data structure, feature type, dataset,
   model architecture, library, framework, metric, equation,
   training procedure, deployment method, or implementation
   technique unless that information is explicitly supported
   by the resume.

10. If a technology or algorithm is mentioned in the resume,
    you may ask about that technology or algorithm. However,
    do not assume that the candidate used additional techniques
    commonly associated with it.

11. If a project is mentioned but the resume does not provide
    implementation details, ask questions that allow the
    candidate to explain those details rather than assuming
    what those details were.

12. General technical knowledge may be tested when it is
    relevant to a technology explicitly mentioned in the
    resume, but the question must not imply that the candidate
    used an unstated technique.

13. Do not invent project details, responsibilities,
    achievements, technologies, metrics, or results.

14. Keep the analysis concise but useful.

15. Do not calculate or invent an ATS score.

16. Do not fabricate achievements or metrics.

17. Return JSON only.

RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}
"""

    response = safe_chat(
        client=client,
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional resume analyst. "
                    "Ground candidate-specific claims strictly "
                    "in the supplied resume. "
                    "Generate interview questions dynamically "
                    "from the supplied resume and job description. "
                    "Never invent candidate experience. "
                    "Return valid JSON only."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1500,
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

    response = safe_chat(
        client=client,
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert resume coach. "
                    "Never invent or fabricate candidate "
                    "achievements or metrics."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=1500,
    )

    return response.choices[0].message.content or ""