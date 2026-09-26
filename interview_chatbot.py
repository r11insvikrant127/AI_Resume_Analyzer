# interview_chatbot.py

import json
import re


SIM_SYSTEM = (
    "You are a professional interviewer conducting a mock "
    "interview for the role described in the job description. "
    "You ask ONE question at a time. After the candidate answers, "
    "you give brief constructive feedback (2-3 sentences), then "
    "ask the next question. Stay on topic. Never invent facts "
    "about the candidate. Never reveal the resume text verbatim."
)

QA_SYSTEM = (
    "You are a career coach helping the candidate prepare for "
    "an interview. Answer their questions clearly and concisely. "
    "Ground every answer in the resume and job description "
    "provided. Never invent experience the candidate does not have. "
    "If a question requires information not present, say so."
)


def _context_block(resume_text, jd_text, prior_questions):
    return f"""
CANDIDATE RESUME:
{resume_text[:6000]}

JOB DESCRIPTION:
{jd_text[:4000]}

EXISTING QUESTION BANK (from analysis):
{json.dumps(prior_questions[:10], indent=2)}
"""


def start_simulation(client, model, resume_text, jd_text, question_bank):
    """
    Returns the first interviewer message.
    """

    prompt = f"""
You are starting a mock interview.

{_context_block(resume_text, jd_text, question_bank)}

Rules:
- Greet the candidate briefly.
- Ask the FIRST interview question.
- Do not ask more than one question.
- Return plain text, not JSON.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SIM_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content or ""


def next_simulation_turn(client, model, resume_text, jd_text,
                         history, candidate_answer):
    """
    Given the chat history (list of {role, content}) and the
    candidate's latest answer, return the interviewer's next
    message (feedback + next question).
    """

    messages = [{"role": "system", "content": SIM_SYSTEM}]

    # Prime with context once
    messages.append({
        "role": "user",
        "content": (
            "Context for the interview:\n"
            + _context_block(resume_text, jd_text, [])
        ),
    })
    messages.append({
        "role": "assistant",
        "content": "Understood. I will conduct the interview now.",
    })

    # Full transcript
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})

    # Latest candidate answer
    messages.append({"role": "user", "content": candidate_answer})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.4,
    )

    return response.choices[0].message.content or ""


def answer_question(client, model, resume_text, jd_text,
                    history, user_question):
    """
    Q&A mode: candidate asks, we answer.
    """

    messages = [{"role": "system", "content": QA_SYSTEM}]

    messages.append({
        "role": "user",
        "content": (
            "Context:\n" + _context_block(resume_text, jd_text, [])
        ),
    })
    messages.append({
        "role": "assistant",
        "content": "Got it. Ask me anything.",
    })

    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})

    messages.append({"role": "user", "content": user_question})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content or ""