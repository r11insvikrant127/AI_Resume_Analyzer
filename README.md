# AI Resume Analyzer & Job Matcher

A Streamlit application that compares a candidate's resume (PDF)
against a job description and produces:

- A transparent, deterministic **ATS score**
- **Keyword matching** for required and good-to-have keywords
- **Technical skill matching** (matched / partial / missing)
- **Skill-gap analysis** with priorities
- Qualitative feedback (summary, strengths, weaknesses,
  resume improvements, interview questions)

The key design principle: **the LLM never determines the score
or the skill classification.** Those are done deterministically
in Python. The LLM is used only for narrative and for parsing
the job description into required / good-to-have keywords.

---

## 1. Project Overview

Most "AI resume checkers" ask an LLM for a score, which makes
the score non-reproducible. This project separates concerns:

| Concern | Handled by |
|---|---|
| JD → required / good-to-have keywords | Groq LLM (once per JD) |
| Skill matched / partial / missing | Deterministic Python |
| Skill-gap priority | Deterministic Python |
| ATS score | Deterministic Python |
| Summary, strengths, weaknesses, improvements, interview Qs | Groq LLM |

---

## 2. Features

- Resume PDF text extraction (`pypdf`)
- Job-description keyword extraction into two buckets
- Deterministic skill matching with **explicit partial-match relations**
  (e.g. Spring Boot ↔ FastAPI, MySQL ↔ SQLite)
- Transparent ATS formula shown in the UI
- Skill-gap analysis split into High Priority / Partial / Good-to-Have
- Session-level JD keyword caching
- LLM-generated interview questions and resume suggestions

---

## 3. Tech Stack

- Python 3.10+
- Streamlit
- Groq API (`groq` Python SDK)
- pypdf
- python-dotenv

---

## 4. Architecture

```
Resume PDF ──► PDF Extraction ──► Resume Text
                                        │
Job Description ────────────────────────┤
                                        ▼
                              ┌──────────────────────┐
                              │ JD Keyword Extractor │
                              │     (Groq LLM)       │
                              └─────────┬────────────┘
                                        │
                        ┌───────────────┴───────────────┐
                        ▼                               ▼
                Required Keywords               Good-to-Have
                        │                               │
                        └───────────────┬───────────────┘
                                        ▼
                              Deterministic Matcher
                                        │
                        ┌───────────────┼───────────────┐
                        ▼               ▼               ▼
                    Matched         Partial         Missing
                        │               │               │
                        └───────────────┼───────────────┘
                                        ▼
                                   ATS Scorer
                                        │
                                        ▼
                                   ATS Score

Resume + JD ──► Groq LLM ──► Qualitative Analysis
                                 (summary, strengths,
                                  weaknesses, improvements,
                                  interview questions)
```

---

## 5. Project Structure

```
AI_Resume_Analyzer/
├── app.py                    # Streamlit application
├── keyword_analyzer.py       # Aliases, taxonomy, deterministic matching, JD extraction
├── ats_scorer.py             # Skill-match + ATS-score formulas
├── skill_gap_analyzer.py     # Deterministic gap presenter
├── requirements.txt
├── .gitignore
├── .env                      # Not committed
└── README.md
```

---

## 6. Installation

```bash
git clone https://github.com/r11insvikrant127/AI_Resume_Analyzer.git
cd AI_Resume_Analyzer

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

---

## 7. Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

`.env` is ignored by git via `.gitignore`.

---

## 8. How to Run

```bash
streamlit run app.py
```

Then open the URL printed in the terminal (usually
`http://localhost:8501`).

---

## 9. How the ATS Score Is Calculated

```
ATS Score =
    Required Keyword Match  × 0.50
  + Technical Skill Match   × 0.40
  + Good-to-Have Match      × 0.10
```

Where:

- **Required Keyword Match** = % of required JD keywords
  found in the resume (aliases respected).
- **Technical Skill Match** = weighted score over *required
  technical* skills only:
  - matched = 1.0
  - partial = 0.5 (only when an **explicit relation** exists,
    e.g. Spring Boot ↔ FastAPI)
  - missing = 0.0
- **Good-to-Have Match** = % of good-to-have JD keywords
  found in the resume.

The exact calculation (with substituted numbers) is displayed
under "How This ATS Score Was Calculated".

---

## 10. Example Workflow

1. Upload a text-based PDF resume.
2. Paste a job description.
3. Click **Analyze Resume**.
4. Review:
   - Headline metrics (ATS Score, Required Keyword Match,
     Technical Skill Match)
   - Explicit score breakdown
   - Required / Good-to-Have keyword lists
   - Technical Skill Match detail
   - Skill Gap Analysis (High Priority / Partial / Good-to-Have)
   - LLM narrative and interview questions

---

## 11. Future Improvements

- Pinned dependency versions for full reproducibility
- Expanded `SKILL_RELATIONS` map (community-maintained)
- Unit tests for `keyword_analyzer` and `ats_scorer`
- Multi-resume batch comparison
- Export report as PDF
- Domain-specific taxonomies (frontend / backend / data / ML)
- Semantic matching (embeddings) as a *secondary* signal,
  never as the primary scoring path