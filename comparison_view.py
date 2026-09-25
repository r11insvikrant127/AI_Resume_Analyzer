# comparison_view.py

import streamlit as st


def render_comparison(results):
    """
    Render the multi-resume comparison table and ranking.

    `results` is a list of analysis dicts produced by
    analyze_single_resume().
    """

    st.header("Resume Comparison")

    ranked = sorted(
        results,
        key=lambda r: r.get("ats_score", 0),
        reverse=True,
    )

    # --------------------------------------------------------
    # Ranking table
    # --------------------------------------------------------

    rows = []

    for rank, r in enumerate(ranked, start=1):
        rows.append({
            "Rank": rank,
            "Resume": r.get("resume_name", "—"),
            "ATS Score": f"{r.get('ats_score', 0)}%",
            "Required Match": f"{r.get('required_match_percentage', 0)}%",
            "Technical Match": f"{r.get('technical_skill_percentage', 0)}%",
            "Good-to-Have": f"{r.get('good_to_have_match_percentage', 0)}%",
        })

    st.dataframe(rows, use_container_width=True)

    # --------------------------------------------------------
    # Winner highlight
    # --------------------------------------------------------

    if ranked:
        best = ranked[0]
        st.success(
            f"🏆 Best match: **{best.get('resume_name')}** "
            f"with an ATS score of **{best.get('ats_score', 0)}%**."
        )

    st.divider()

    # --------------------------------------------------------
    # Side-by-side metrics
    # --------------------------------------------------------

    st.subheader("Score Comparison")

    cols = st.columns(len(ranked)) if ranked else []

    for col, r in zip(cols, ranked):
        with col:
            st.markdown(f"**{r.get('resume_name', '—')}**")
            st.metric("ATS", f"{r.get('ats_score', 0)}%")
            st.metric("Required", f"{r.get('required_match_percentage', 0)}%")
            st.metric("Technical", f"{r.get('technical_skill_percentage', 0)}%")

    st.divider()

    # --------------------------------------------------------
    # Missing-skill overlap
    # --------------------------------------------------------

    st.subheader("Missing Required Skills by Resume")

    for r in ranked:
        st.markdown(f"**{r.get('resume_name', '—')}**")
        missing = r.get("missing_required_requirements", [])
        if missing:
            for s in missing:
                st.write(f"• {s}")
        else:
            st.write("None")
        st.write("")

    st.divider()

    from report_generator import build_comparison_pdf

    try:
        pdf_bytes = build_comparison_pdf(results)

        st.download_button(
            label="⬇️ Download Comparison PDF",
            data=pdf_bytes,
            file_name="resume_comparison_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.warning(f"Could not generate comparison PDF: {e}")