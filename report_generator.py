# report_generator.py

import io
from datetime import datetime

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


# ============================================================
# STYLESHEET (cached, with guarded registration)
# ============================================================

_STYLES_CACHE = None


def _styles():
    """
    Build (once) and return the stylesheet used for report
    generation. Custom styles are registered only if missing.
    """

    global _STYLES_CACHE

    if _STYLES_CACHE is not None:
        return _STYLES_CACHE

    styles = getSampleStyleSheet()

    def _add(name, parent, **kwargs):
        if name in styles.byName:
            return
        styles.add(ParagraphStyle(
            name=name,
            parent=styles[parent],
            **kwargs,
        ))

    _add(
        "SectionHeader",
        "Heading2",
        spaceBefore=14,
        spaceAfter=6,
        textColor=colors.HexColor("#1f3a5f"),
    )

    _add(
        "SubHeader",
        "Heading3",
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.HexColor("#2c5282"),
    )

    _add(
        "Body",
        "BodyText",
        leading=14,
        spaceAfter=4,
    )

    _add(
        "Bullet",
        "BodyText",
        leftIndent=14,
        bulletIndent=4,
        leading=14,
        spaceAfter=2,
    )

    _STYLES_CACHE = styles
    return styles


# ============================================================
# METRIC TABLE
# ============================================================

def _metric_table(result):
    data = [
        ["Metric", "Score"],
        ["ATS Score", f"{result.get('ats_score', 0)}%"],
        ["Required Requirement Match",
         f"{result.get('required_match_percentage', 0)}%"],
        ["Technical Skill Match",
         f"{result.get('technical_skill_percentage', 0)}%"],
        ["Good-to-Have Match",
         f"{result.get('good_to_have_match_percentage', 0)}%"],
    ]

    table = Table(data, colWidths=[4 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#f0f4f8")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    return table


# ============================================================
# LIST HELPERS
# ============================================================

def _bullet_list(items, style):
    flow = []
    if not items:
        flow.append(Paragraph("None", style))
        return flow
    for item in items:
        flow.append(Paragraph(f"• {item}", style))
    return flow


def _numbered_list(items, style):
    flow = []
    if not items:
        flow.append(Paragraph("None", style))
        return flow
    for i, item in enumerate(items, start=1):
        flow.append(Paragraph(f"{i}. {item}", style))
    return flow


# ============================================================
# SINGLE-RESUME REPORT
# ============================================================

def build_pdf_report(result):
    """
    Build a single-resume PDF report and return it as bytes.
    """

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="AI Resume Analysis Report",
    )

    s = _styles()
    flow = []

    resume_name = result.get("resume_name", "Resume")

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    flow.append(Paragraph("AI Resume Analysis Report", s["Title"]))
    flow.append(Paragraph(f"Resume: <b>{resume_name}</b>", s["Body"]))
    flow.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        s["Body"],
    ))
    flow.append(Spacer(1, 12))

    # --------------------------------------------------------
    # Scores
    # --------------------------------------------------------

    flow.append(Paragraph("Score Summary", s["SectionHeader"]))
    flow.append(_metric_table(result))
    flow.append(Spacer(1, 10))

    # --------------------------------------------------------
    # Candidate summary
    # --------------------------------------------------------

    flow.append(Paragraph("Candidate Summary", s["SectionHeader"]))
    flow.append(Paragraph(
        result.get("candidate_summary", "Not available."),
        s["Body"],
    ))

    # --------------------------------------------------------
    # Strengths / Weaknesses
    # --------------------------------------------------------

    flow.append(Paragraph("Strengths", s["SectionHeader"]))
    flow.extend(_bullet_list(result.get("strengths", []), s["Bullet"]))

    flow.append(Paragraph("Weaknesses", s["SectionHeader"]))
    flow.extend(_bullet_list(result.get("weaknesses", []), s["Bullet"]))

    flow.append(PageBreak())

    # --------------------------------------------------------
    # Requirement matching
    # --------------------------------------------------------

    flow.append(Paragraph("Required Requirements", s["SectionHeader"]))

    flow.append(Paragraph("Matched", s["SubHeader"]))
    flow.extend(_bullet_list(
        result.get("matched_required_requirements", []),
        s["Bullet"],
    ))

    flow.append(Paragraph("Partial", s["SubHeader"]))
    flow.extend(_bullet_list(
        result.get("partial_required_requirements", []),
        s["Bullet"],
    ))

    flow.append(Paragraph("Missing", s["SubHeader"]))
    flow.extend(_bullet_list(
        result.get("missing_required_requirements", []),
        s["Bullet"],
    ))

    # --------------------------------------------------------
    # ATS keyword analysis (Feature 1)
    # --------------------------------------------------------

    kw = result.get("ats_keyword_analysis", {}) or {}
    kw_rows = kw.get("keyword_rows", [])

    if kw_rows:

        flow.append(Paragraph("ATS Keyword Analysis", s["SectionHeader"]))

        flow.append(Paragraph(
            f"Required Keyword Coverage: "
            f"{kw.get('required_coverage', 0)}%",
            s["Body"],
        ))

        kw_table_data = [["Keyword", "Tier", "Count", "Per 1k"]]
        for r in kw_rows:
            kw_table_data.append([
                r["keyword"],
                r["tier"],
                str(r["count"]),
                str(r["density_per_1000"]),
            ])

        kw_table = Table(
            kw_table_data,
            colWidths=[3 * inch, 1.2 * inch, 0.8 * inch, 1 * inch],
        )
        kw_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#f0f4f8")]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        flow.append(kw_table)

    # --------------------------------------------------------
    # Skill gap
    # --------------------------------------------------------

    gap = result.get("skill_gap", {}) or {}

    flow.append(Paragraph("Skill Gap Analysis", s["SectionHeader"]))

    flow.append(Paragraph("High-Priority Gaps", s["SubHeader"]))
    flow.extend(_bullet_list(gap.get("high_priority_gaps", []), s["Bullet"]))

    flow.append(Paragraph("Partial Required Skills", s["SubHeader"]))
    flow.extend(_bullet_list(gap.get("partial_matches", []), s["Bullet"]))

    flow.append(Paragraph("Good-to-Have Gaps", s["SubHeader"]))
    flow.extend(_bullet_list(gap.get("good_to_have_gaps", []), s["Bullet"]))

    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    flow.append(Paragraph("Resume Improvements", s["SectionHeader"]))
    flow.extend(_numbered_list(
        result.get("resume_improvements", []),
        s["Bullet"],
    ))

    flow.append(Paragraph("Interview Questions", s["SectionHeader"]))
    flow.extend(_numbered_list(
        result.get("interview_questions", []),
        s["Bullet"],
    ))

    doc.build(flow)

    return buffer.getvalue()


# ============================================================
# COMPARISON REPORT (with composite ranking — Feature 2)
# ============================================================

def build_comparison_pdf(results):
    """
    Build a ranked comparison PDF for multiple resumes.

    `results` may either be already-ranked (containing
    'rank' and 'composite_score') or unranked; unranked
    entries are ranked with default weights.
    """

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="Resume Comparison Report",
    )

    s = _styles()
    flow = []

    flow.append(Paragraph("Resume Comparison Report", s["Title"]))
    flow.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        s["Body"],
    ))
    flow.append(Spacer(1, 12))

    # --------------------------------------------------------
    # Ensure ranked
    # --------------------------------------------------------

    if results and "composite_score" not in results[0]:
        from candidate_ranker import rank_candidates
        ranked = rank_candidates(results)
    else:
        ranked = results

    data = [[
        "Rank", "Resume", "Composite", "ATS", "Required",
        "Technical", "Good-to-Have",
    ]]

    for r in ranked:
        data.append([
            str(r.get("rank", 0)),
            r.get("resume_name", "—"),
            f"{r.get('composite_score', 0)}%",
            f"{r.get('ats_score', 0)}%",
            f"{r.get('required_match_percentage', 0)}%",
            f"{r.get('technical_skill_percentage', 0)}%",
            f"{r.get('good_to_have_match_percentage', 0)}%",
        ])

    table = Table(
        data,
        colWidths=[0.5 * inch, 1.9 * inch, 0.9 * inch,
                   0.7 * inch, 0.8 * inch, 0.8 * inch, 0.9 * inch],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#f0f4f8")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    flow.append(table)

    # --------------------------------------------------------
    # Winner callout
    # --------------------------------------------------------

    if ranked:
        best = ranked[0]
        flow.append(Spacer(1, 10))
        flow.append(Paragraph(
            f"<b>Best candidate:</b> "
            f"{best.get('resume_name', '—')} "
            f"(composite {best.get('composite_score', 0)}%)",
            s["Body"],
        ))

    doc.build(flow)

    return buffer.getvalue()