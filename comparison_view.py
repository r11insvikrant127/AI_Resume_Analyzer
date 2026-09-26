# comparison_view.py

import streamlit as st

from candidate_ranker import rank_candidates, DEFAULT_WEIGHTS


def render_comparison(results, client=None, model=None):
    """
    Render the multi-resume comparison table and ranking.

    Parameters
    ----------
    results : list
        List of analysis dicts produced by
        analyze_single_resume().

    client, model :
        Optional Groq client + model name. When supplied,
        the drill-down can render the rewrite / tips
        expanders for the selected resume. When omitted,
        the drill-down shows a report without extras.
    """

    st.header("Resume Comparison")

    # --------------------------------------------------------
    # Ranking weights
    # --------------------------------------------------------

    st.subheader("Ranking Weights")

    w_ats = st.slider(
        "ATS Score",
        0.0, 1.0,
        DEFAULT_WEIGHTS["ats_score"],
        0.05,
    )
    w_req = st.slider(
        "Required Match",
        0.0, 1.0,
        DEFAULT_WEIGHTS["required_match_percentage"],
        0.05,
    )
    w_tech = st.slider(
        "Technical Match",
        0.0, 1.0,
        DEFAULT_WEIGHTS["technical_skill_percentage"],
        0.05,
    )
    w_good = st.slider(
        "Good-to-Have",
        0.0, 1.0,
        DEFAULT_WEIGHTS["good_to_have_match_percentage"],
        0.05,
    )
    w_kw = st.slider(
        "Keyword Coverage",
        0.0, 1.0,
        DEFAULT_WEIGHTS["keyword_coverage"],
        0.05,
    )

    weights = {
        "ats_score": w_ats,
        "required_match_percentage": w_req,
        "technical_skill_percentage": w_tech,
        "good_to_have_match_percentage": w_good,
        "keyword_coverage": w_kw,
    }

    ranked = rank_candidates(results, weights)

    # --------------------------------------------------------
    # Ranking table
    # --------------------------------------------------------

    rows = []

    for r in ranked:

        kw_cov = (
            r.get("ats_keyword_analysis", {}) or {}
        ).get("required_coverage", 0)

        rows.append({
            "Rank": r["rank"],
            "Resume": r.get("resume_name", "—"),
            "Composite": f"{r['composite_score']}%",
            "ATS": f"{r.get('ats_score', 0)}%",
            "Required": f"{r.get('required_match_percentage', 0)}%",
            "Technical": f"{r.get('technical_skill_percentage', 0)}%",
            "Good-to-Have": f"{r.get('good_to_have_match_percentage', 0)}%",
            "Keyword Cov": f"{kw_cov}%",
        })

    st.dataframe(rows, use_container_width=True)

    # --------------------------------------------------------
    # Winner highlight
    # --------------------------------------------------------

    if ranked:

        best = ranked[0]

        st.success(
            f"🏆 Best candidate: **{best.get('resume_name')}** "
            f"(composite {best['composite_score']}%)"
        )

    st.divider()

    # --------------------------------------------------------
    # Side-by-side metrics
    # --------------------------------------------------------

    st.subheader("Score Comparison")

    cols = st.columns(len(ranked)) if ranked else []

    for col, r in zip(cols, ranked):
        with col:
            st.markdown(
                f"**#{r['rank']} — {r.get('resume_name', '—')}**"
            )
            st.metric("Composite", f"{r['composite_score']}%")
            st.metric("ATS", f"{r.get('ats_score', 0)}%")
            st.metric("Required", f"{r.get('required_match_percentage', 0)}%")
            st.metric("Technical", f"{r.get('technical_skill_percentage', 0)}%")

    st.divider()

    # --------------------------------------------------------
    # Missing-skill overlap
    # --------------------------------------------------------

    st.subheader("Missing Required Skills by Resume")

    for r in ranked:

        st.markdown(
            f"**#{r['rank']} — {r.get('resume_name', '—')}**"
        )

        missing = r.get("missing_required_requirements", [])

        if missing:
            for s in missing:
                st.write(f"• {s}")
        else:
            st.write("None")

        st.write("")

    st.divider()

    # --------------------------------------------------------
    # Full per-resume report drill-down
    # --------------------------------------------------------

    st.subheader("Full Report Drill-Down")

    names = [r.get("resume_name", "—") for r in ranked]

    if names:

        selected = st.selectbox(
            "Choose a resume to view its full report",
            options=range(len(names)),
            format_func=lambda i: names[i],
            key="comparison_drilldown",
        )

        selected_result = ranked[selected]

        with st.expander(
            f"Full report: {selected_result.get('resume_name', '—')}",
            expanded=True,
        ):
            from report_view import render_single_report

            render_single_report(
                selected_result,
                client=client,
                model=model,
                show_pdf_download=True,
                # Do not duplicate rewrite / tips expanders here;
                # the top-level single-report view already renders them.
                show_extras=False,
            )

    st.divider()

    # --------------------------------------------------------
    # Comparison PDF
    # --------------------------------------------------------

    from report_generator import build_comparison_pdf

    try:
        pdf_bytes = build_comparison_pdf(ranked)

        st.download_button(
            label="⬇️ Download Comparison PDF",
            data=pdf_bytes,
            file_name="resume_comparison_report.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="comparison_pdf_download",
        )
    except Exception as e:
        st.warning(f"Could not generate comparison PDF: {e}")