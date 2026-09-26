# interview_chatbot.py

import json


SIM_SYSTEM = """
You are a professional interviewer conducting a mock interview
for the role described in the job description.

Your job is to test the candidate's actual experience and knowledge.

STRICT GROUNDING RULES:

1. Treat the candidate's resume as the source of truth about their
   projects, experience, technologies, responsibilities, and
   achievements.

2. NEVER invent or assume implementation details that are not explicitly
   present in the resume or additional project context provided by the
   candidate.

3. Do NOT infer specific:
   - algorithms
   - data structures
   - feature extraction techniques
   - model architectures
   - datasets
   - libraries/frameworks
   - evaluation metrics
   - accuracy/precision/recall values
   - equations
   - training procedures
   - deployment methods
   - implementation steps
   - performance improvements
   merely because they are commonly associated with a technology.

4. If the resume mentions a technology or algorithm, that does NOT mean
   every standard technique associated with it was used by the candidate.

5. For example, if the resume says that a project used pLSA with
   appropriate video features, do NOT assume which specific features,
   topic inference procedure, clustering algorithm, probability
   equations, evaluation metrics, or implementation details were used.

6. If the resume does not contain enough information to answer a
   technical question about the candidate's implementation, explicitly
   say:

   "The resume does not provide that level of implementation detail."

7. You may explain GENERAL technical concepts when the candidate asks
   for them, but clearly distinguish general knowledge from the
   candidate's actual implementation.

8. Never present a general explanation of a technology as something
   the candidate personally implemented.

9. Do not treat technologies or requirements mentioned only in the job
   description as technologies the candidate has experience with.

10. Do not treat questions in the existing question bank as evidence
    that the candidate has experience with the technologies mentioned
    in those questions.

11. Never reveal the resume text verbatim.

12. Ask ONE question at a time.

13. After the candidate answers, provide brief constructive feedback
    in 2-3 sentences and then ask exactly ONE follow-up question.

14. Stay relevant to the candidate's resume and the target job.
"""


QA_SYSTEM = """
You are a career coach helping a candidate prepare for an interview.

STRICT GROUNDING RULES:

1. The candidate's resume is the source of truth for the candidate's
   personal experience.

2. Ground claims about the candidate ONLY in information explicitly
   present in the resume, job description, or additional project
   context provided by the candidate.

3. NEVER invent or assume details about how the candidate implemented
   something.

4. Do NOT infer specific:
   - algorithms
   - data structures
   - feature types
   - datasets
   - models
   - libraries/frameworks
   - metrics
   - equations
   - architectures
   - training procedures
   - implementation steps
   - performance results
   unless they are explicitly provided.

5. Common technical knowledge must NOT be converted into a claim about
   the candidate.

6. If the question asks about the candidate's own implementation,
   challenge, solution, decision, optimization, methodology, or
   results, and the resume does not provide enough information,
   say:

   "The resume does not provide that level of implementation detail."

   Do NOT provide hypothetical implementation details, possible
   challenges, possible solutions, or likely techniques that the
   candidate may have used.

7. Only provide a GENERAL technical explanation when the candidate
   explicitly asks for general technical knowledge rather than asking
   what they personally did.

8. If a question is ambiguous between the candidate's experience and
   general technical knowledge, prioritize the candidate's documented
   experience. If the resume does not contain enough information,
   state that the information is unavailable instead of guessing.

9. When helping formulate an interview answer, separate:
   - What the resume explicitly supports
   - What the candidate should explain from their actual experience

10. Never fabricate achievements, responsibilities, technologies,
   metrics, project details, or experience.

11. Do not treat technologies mentioned only in the job description as
    skills the candidate possesses.

12. Do not treat questions from the existing question bank as evidence
    that the candidate has used the technologies mentioned in those
    questions.

13. Never reveal the resume text verbatim.
"""


def _context_block(resume_text, jd_text, prior_questions):
    """
    Builds the grounding context supplied to the LLM.

    The resume is the source of truth for candidate-specific claims.
    The JD describes the target role, not the candidate's experience.
    The question bank contains questions, not evidence of experience.
    """

    return f"""
SOURCE OF TRUTH — CANDIDATE RESUME:

The following text contains information about the candidate.

Only claims explicitly supported by this text may be attributed
to the candidate.

--- RESUME START ---
{resume_text[:6000]}
--- RESUME END ---


SOURCE OF TRUTH — JOB DESCRIPTION:

The following describes the target role and its requirements.

Do NOT treat requirements in the JD as evidence that the candidate
has those skills or experience.

--- JOB DESCRIPTION START ---
{jd_text[:4000]}
--- JOB DESCRIPTION END ---


EXISTING INTERVIEW QUESTION BANK:

These are questions generated from the previous analysis.

They are questions only. They must NOT be treated as evidence that
the candidate has experience with the technologies or topics mentioned
in them.

--- QUESTION BANK START ---
{json.dumps(prior_questions[:10], indent=2)}
--- QUESTION BANK END ---
"""


def start_simulation(client, model, resume_text, jd_text, question_bank):
    """
    Returns the first interviewer message.
    """

    prompt = f"""
You are starting a mock interview.

{_context_block(resume_text, jd_text, question_bank)}

Rules for this turn:

- Greet the candidate briefly.
- Ask the FIRST interview question.
- Prefer questions about projects, skills, or experience explicitly
  supported by the resume.
- If asking about something mentioned only in the job description,
  make it clear that you are asking about the candidate's exposure
  rather than assuming they have that experience.
- Do not assume implementation details that are not documented.
- Do not ask more than one question.
- Return plain text, not JSON.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SIM_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content or ""


def next_simulation_turn(
    client,
    model,
    resume_text,
    jd_text,
    history,
    candidate_answer,
):
    """
    Given the chat history and the candidate's latest answer,
    return feedback followed by the next interview question.
    """

    messages = [{"role": "system", "content": SIM_SYSTEM}]

    # Provide the grounding context.
    messages.append({
        "role": "user",
        "content": (
            "Context for the interview:\n"
            + _context_block(resume_text, jd_text, [])
        ),
    })

    messages.append({
        "role": "assistant",
        "content": "Understood. I will conduct the interview using only the supported candidate information.",
    })

    # Add the previous transcript.
    for m in history:
        messages.append({
            "role": m["role"],
            "content": m["content"],
        })

    # Give the model the candidate's latest answer together with
    # explicit grounding instructions.
    messages.append({
        "role": "user",
        "content": f"""
Evaluate the candidate's latest interview answer.

IMPORTANT:

- Evaluate the answer against the candidate's actual resume.
- Do not assume that technical details mentioned by the candidate
  are true merely because they are plausible.
- If the candidate claims an implementation detail that is not
  supported by the resume, do not reinforce it as established fact.
- Give brief constructive feedback in 2-3 sentences.
- Then ask exactly ONE relevant follow-up interview question.
- The follow-up question should preferably explore something
  explicitly supported by the resume.
- Do not invent additional project details.

Candidate's latest answer:
--- ANSWER START ---
{candidate_answer}
--- ANSWER END ---
""",
    })

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content or ""


def answer_question(
    client,
    model,
    resume_text,
    jd_text,
    history,
    user_question,
):
    """
    Q&A mode: candidate asks an interview-preparation question
    and the assistant answers using the resume/JD context.
    """

    messages = [{"role": "system", "content": QA_SYSTEM}]

    messages.append({
        "role": "user",
        "content": (
            "Context for the interview:\n"
            + _context_block(resume_text, jd_text, [])
        ),
    })

    messages.append({
        "role": "assistant",
        "content": (
            "Understood. I will distinguish the candidate's documented "
            "experience from general technical explanations."
        ),
    })

    # Add previous conversation.
    for m in history:
        messages.append({
            "role": m["role"],
            "content": m["content"],
        })

    # Current question.
    messages.append({
        "role": "user",
        "content": f"""
Answer the candidate's question.

Before answering, determine whether the question asks about:

A) Something explicitly documented in the candidate's resume,
B) Something that requires information not present in the resume, or
C) A general technical concept.

Rules:

- For A: answer using only the documented information.
- For B: explicitly state that the resume does not provide enough
  implementation detail.
- For C: provide a general explanation and clearly label it
  "General concept".
- Never turn general technical knowledge into a claim about the
  candidate's personal experience.
- Never invent project details.

Candidate question:
{user_question}
""",
    })

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
    )

    return response.choices[0].message.content or ""