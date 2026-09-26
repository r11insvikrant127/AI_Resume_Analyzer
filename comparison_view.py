# comparison_view.py

import streamlit as st

from candidate_ranker import rank_candidates, DEFAULT_WEIGHTS
from styles import section, score_card


def render_comparison(results, client=None, model=None):

    # --------------------------------------------------------
    # Ranking weights
    # --------------------------------------------------------

    section("⚖️", "Ranking Weights", "Tune how candidates are scored")

    with st.container(border=True):

        w1, w2, w3 = st.columns(3)
        with w1:
            w_ats = st.slider(
                "ATS Score", 0.0, 1.0,
                DEFAULT_WEIGHTS["ats_score"], 0.05,
            )
            w_req = st.slider(
                "Required Match", 0.0, 1.0,
                DEFAULT_WEIGHTS["required_match_percentage"], 0.05,
            )
        with w2:
            w_tech = st.slider(
                "Technical Match", 0.0, 1.0,
                DEFAULT_WEIGHTS["technical_skill_percentage"], 0.05,
            )
            w_good = st.slider(
                "Good-to-Have", 0.0, 1.0,
                DEFAULT_WEIGHTS["good_to_have_match_percentage"], 0.05,
            )
        with w3:
            w_kw = st.slider(
                "Keyword Coverage", 0.0, 1.0,
                DEFAULT_WEIGHTS["keyword_coverage"], 0.05,
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
    # Winner banner
    # --------------------------------------------------------

    if ranked:
        best = ranked[0]
        st.success(
            f"🏆 **Best candidate: {best.get('resume_name')}** "
            f"— composite score **{best['composite_score']}%**"
        )

    # --------------------------------------------------------
    # Ranking table
    # --------------------------------------------------------

    section("📋", "Ranking Table")

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

    st.dataframe(rows, use_container_width=True, hide_index=True)

    # --------------------------------------------------------
    # Side-by-side
    # --------------------------------------------------------

    section("📊", "Score Comparison")

    cols = st.columns(len(ranked)) if ranked else []

    for col, r in zip(cols, ranked):
        with col:
            st.markdown(
                f"**#{r['rank']} · {r.get('resume_name', '—')}**"
            )
            score_card(
                "Composite",
                r["composite_score"],
                "weighted overall",
            )
            score_card("ATS", r.get("ats_score", 0))
            score_card("Required", r.get("required_match_percentage", 0))
            score_card("Technical", r.get("technical_skill_percentage", 0))

    # --------------------------------------------------------
    # Missing skills
    # --------------------------------------------------------

    section("⚠️", "Missing Required Skills by Resume")

    for r in ranked:
        with st.container(border=True):
            st.markdown(
                f"**#{r['rank']} · {r.get('resume_name', '—')}**"
            )
            missing = r.get("missing_required_requirements", [])
            if missing:
                st.markdown(
                    " ".join(
                        f'<span class="chip missing">{m}</span>'
                        for m in missing
                    ),
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No missing required skills.")

    # --------------------------------------------------------
    # Drill-down
    # --------------------------------------------------------

    section("🔍", "Full Report Drill-Down")

    names = [r.get("resume_name", "—") for r in ranked]

    if names:
        selected = st.selectbox(
            "Choose a resume",
            options=range(len(names)),
            format_func=lambda i: names[i],
            key="comparison_drilldown",
        )

        selected_result = ranked[selected]

        with st.expander(
            f"Full report · {selected_result.get('resume_name', '—')}",
            expanded=True,
        ):
            from report_view import render_single_report
            render_single_report(
                selected_result,
                client=client,
                model=model,
                show_pdf_download=True,
                show_extras=False,
            )

    # --------------------------------------------------------
    # Comparison PDF
    # --------------------------------------------------------

    section("⬇️", "Export")

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