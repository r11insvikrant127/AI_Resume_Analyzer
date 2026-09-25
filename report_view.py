# report_view.py

import streamlit as st


def render_single_report(
    result,
    client=None,
    model=None,
    show_pdf_download=True,
    show_extras=True,
):
    """
    Render a complete single-resume report.

    Parameters
    ----------
    result : dict
        Output of analyze_single_resume().

    client, model :
        Groq client and model name. Required if
        show_extras=True and the user clicks the
        rewrite / tips buttons.

    show_pdf_download : bool
        Render a per-resume PDF download button.
        Set False when app.py renders its own.

    show_extras : bool
        Render the rewrite expander and general tips
        expander. Set False for the comparison
        drill-down (to avoid duplicate widget keys).
    """

    # --------------------------------------------------------
    # HEADLINE METRICS
    # --------------------------------------------------------

    score = result.get("ats_score", 0)
    required_score = result.get("required_match_percentage", 0)
    technical_score = result.get("technical_skill_percentage", 0)
    good_to_have_score = result.get("good_to_have_match_percentage", 0)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("ATS Score", f"{score}%")
    with c2:
        st.metric("Required Requirement Match", f"{required_score}%")
    with c3:
        st.metric("Technical Skill Match", f"{technical_score}%")

    st.progress(min(max(score, 0), 100) / 100)

    # --------------------------------------------------------
    # SCORE CALCULATION
    # --------------------------------------------------------

    st.subheader("How This ATS Score Was Calculated")

    req_contribution = round(required_score * 0.50, 2)
    technical_contribution = round(technical_score * 0.40, 2)
    good_to_have_contribution = round(good_to_have_score * 0.10, 2)

    st.markdown(
        f"""
        <div class="formula">

        Required Requirement Match :
        {required_score}% × 0.50 = {req_contribution}

        <br>

        Technical Skill Match :
        {technical_score}% × 0.40 = {technical_contribution}

        <br>

        Good-to-Have Match :
        {good_to_have_score}% × 0.10 = {good_to_have_contribution}

        <hr>

        <b>Final ATS Score = {score}%</b>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # REQUIREMENT ANALYSIS
    # --------------------------------------------------------

    st.subheader("Job Requirement Analysis")

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric("Required Match", f"{required_score}%")
    with r2:
        st.metric("Good-to-Have Match", f"{good_to_have_score}%")
    with r3:
        overall_requirement_score = round(
            (required_score + good_to_have_score) / 2
        )
        st.metric(
            "Overall Requirement Match",
            f"{overall_requirement_score}%",
        )

    # --------------------------------------------------------
    # REQUIRED REQUIREMENTS
    # --------------------------------------------------------

    st.markdown("### Required Requirements")

    rc1, rc2, rc3 = st.columns(3)

    with rc1:
        st.markdown("#### Matched")
        items = result.get("matched_required_requirements", [])
        if items:
            for x in items:
                st.write(f"✓ {x}")
        else:
            st.write("No required requirements matched.")

    with rc2:
        st.markdown("#### Partial")
        items = result.get("partial_required_requirements", [])
        if items:
            for x in items:
                st.write(f"~ {x}")
        else:
            st.write("No partial required matches.")

    with rc3:
        st.markdown("#### Missing")
        items = result.get("missing_required_requirements", [])
        if items:
            for x in items:
                st.write(f"• {x}")
        else:
            st.write("No required requirements are missing.")

    # --------------------------------------------------------
    # GOOD-TO-HAVE REQUIREMENTS
    # --------------------------------------------------------

    st.markdown("### Good-to-Have Requirements")

    gc1, gc2, gc3 = st.columns(3)

    with gc1:
        st.markdown("#### Matched")
        items = result.get("matched_good_to_have_requirements", [])
        if items:
            for x in items:
                st.write(f"✓ {x}")
        else:
            st.write("No good-to-have requirements matched.")

    with gc2:
        st.markdown("#### Partial")
        items = result.get("partial_good_to_have_requirements", [])
        if items:
            for x in items:
                st.write(f"~ {x}")
        else:
            st.write("No partial good-to-have matches.")

    with gc3:
        st.markdown("#### Missing")
        items = result.get("missing_good_to_have_requirements", [])
        if items:
            for x in items:
                st.write(f"• {x}")
        else:
            st.write("No good-to-have requirements are missing.")

    # --------------------------------------------------------
    # TECHNICAL SKILL MATCH
    # --------------------------------------------------------

    st.subheader("Technical Skill Match Detail")

    st.caption(
        "This component considers required technical "
        "skills only. Categories are determined from "
        "the job description."
    )

    technical_matched = result.get("technical_matched_skills", [])
    technical_partial = result.get("technical_partial_skills", [])
    technical_missing = result.get("technical_missing_skills", [])

    total_technical_skills = (
        len(technical_matched)
        + len(technical_partial)
        + len(technical_missing)
    )

    t1, t2 = st.columns(2)

    with t1:
        st.metric("Technical Skill Match", f"{technical_score}%")
    with t2:
        st.metric("Required Technical Skills", total_technical_skills)

    tc1, tc2, tc3 = st.columns(3)

    with tc1:
        st.markdown("#### Matched Technical")
        if technical_matched:
            for skill in technical_matched:
                st.write(f"✓ {skill}")
        else:
            st.write("None")

    with tc2:
        st.markdown("#### Partial Technical")
        if technical_partial:
            for skill in technical_partial:
                st.write(f"~ {skill}")
        else:
            st.write("None")

    with tc3:
        st.markdown("#### Missing Technical")
        if technical_missing:
            for skill in technical_missing:
                st.write(f"• {skill}")
        else:
            st.write("None")

    # --------------------------------------------------------
    # ATS KEYWORD ANALYSIS
    # --------------------------------------------------------

    st.subheader("🔑 ATS Keyword Analysis")

    ats_kw = result.get("ats_keyword_analysis", {}) or {}
    kw_rows = ats_kw.get("keyword_rows", [])

    if kw_rows:

        kc1, kc2 = st.columns(2)

        with kc1:
            st.metric(
                "Required Keyword Coverage",
                f"{ats_kw.get('required_coverage', 0)}%",
            )
        with kc2:
            st.metric(
                "Resume Word Count",
                ats_kw.get("total_words", 0),
            )

        st.dataframe(
            [
                {
                    "Keyword": r["keyword"],
                    "Tier": r["tier"],
                    "Count": r["count"],
                    "Per 1k Words": r["density_per_1000"],
                    "Top of Resume": "✓" if r["in_top_quarter"] else "—",
                    "In Skills Section": "✓" if r["in_skills_section"] else "—",
                }
                for r in kw_rows
            ],
            use_container_width=True,
        )

        checks = ats_kw.get("checks", {})

        st.markdown("**Formatting checks**")
        st.write(
            f"- Word count: {checks.get('word_count', 0)} "
            f"({'OK' if checks.get('word_count_ok') else 'out of range'})"
        )
        st.write(
            f"- Email present: {'✓' if checks.get('has_email') else '—'}"
        )
        st.write(
            f"- Phone present: {'✓' if checks.get('has_phone') else '—'}"
        )
        st.write(
            f"- Skills section detected: "
            f"{'✓' if checks.get('has_skills_section') else '—'}"
        )

    else:
        st.write("No keyword analysis available.")

    # --------------------------------------------------------
    # NON-TECHNICAL REQUIREMENTS
    # --------------------------------------------------------

    st.subheader("Other Required Skills")

    st.caption(
        "These requirements are part of the job description "
        "but are not included in the Technical Skill Match."
    )

    required_non_technical = result.get("required_non_technical_skills", [])
    nt_matched = result.get("non_technical_matched_skills", [])
    nt_partial = result.get("non_technical_partial_skills", [])
    nt_missing = result.get("non_technical_missing_skills", [])

    if required_non_technical:
        for skill in required_non_technical:
            if skill in nt_matched:
                st.write(f"✓ {skill}")
            elif skill in nt_partial:
                st.write(f"~ {skill}")
            elif skill in nt_missing:
                st.write(f"• {skill}")
    else:
        st.write(
            "No non-technical or foundational requirements "
            "were identified."
        )

    # --------------------------------------------------------
    # SKILL GAP ANALYSIS
    # --------------------------------------------------------

    st.subheader("Skill Gap Analysis")

    skill_gap = result.get("skill_gap", {}) or {}

    st.markdown("### 🔴 High-Priority Skill Gaps")
    high_priority = skill_gap.get("high_priority_gaps", [])
    if high_priority:
        for skill in high_priority:
            st.write(f"• {skill}")
    else:
        st.write("No major required skill gaps identified.")

    st.markdown("### 🟡 Partial Required Skills")
    partial_gaps = skill_gap.get("partial_matches", [])
    if partial_gaps:
        for skill in partial_gaps:
            st.write(f"~ {skill}")
    else:
        st.write("No partial required-skill matches identified.")

    st.markdown("### 🔵 Good-to-Have Gaps")
    good_gaps = skill_gap.get("good_to_have_gaps", [])
    if good_gaps:
        for skill in good_gaps:
            st.write(f"• {skill}")
    else:
        st.write("No good-to-have gaps identified.")

    if skill_gap.get("priority_gaps"):

        st.markdown("### 📊 Coverage")

        cv1, cv2, cv3 = st.columns(3)

        with cv1:
            st.metric(
                "Required Coverage",
                f"{skill_gap.get('required_coverage', 0)}%",
            )
        with cv2:
            st.metric(
                "Optional Coverage",
                f"{skill_gap.get('optional_coverage', 0)}%",
            )
        with cv3:
            st.metric(
                "Severity",
                skill_gap.get("overall_severity", "low").title(),
            )

        st.markdown("### 🎯 Prioritized Gap List")

        for gap in skill_gap["priority_gaps"]:
            icon = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🔵",
            }.get(gap["severity"], "•")

            st.write(
                f"{icon} **{gap['skill']}** — "
                f"{gap['type'].replace('_', ' ')} / {gap['status']}"
            )

    # --------------------------------------------------------
    # CANDIDATE SUMMARY
    # --------------------------------------------------------

    st.subheader("Candidate Summary")
    st.write(result.get("candidate_summary", "No summary available."))

    # --------------------------------------------------------
    # STRENGTHS / WEAKNESSES
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Strengths")
        strengths = result.get("strengths", [])
        if strengths:
            for item in strengths:
                st.write(f"✓ {item}")
        else:
            st.write("No strengths identified.")

    with col2:
        st.subheader("Weaknesses")
        weaknesses = result.get("weaknesses", [])
        if weaknesses:
            for item in weaknesses:
                st.write(f"• {item}")
        else:
            st.write("No weaknesses identified.")

    # --------------------------------------------------------
    # EXPERIENCE / EDUCATION / PROJECT
    # --------------------------------------------------------

    st.subheader("Experience Match")
    st.write(result.get("experience_match", "Not available."))

    st.subheader("Education Match")
    st.write(result.get("education_match", "Not available."))

    st.subheader("Project Match")
    st.write(result.get("project_match", "Not available."))

    # --------------------------------------------------------
    # RESUME IMPROVEMENTS
    # --------------------------------------------------------

    st.subheader("Resume Improvement Recommendations")

    improvements = result.get("resume_improvements", [])
    if improvements:
        for i, item in enumerate(improvements, start=1):
            st.write(f"{i}. {item}")
    else:
        st.write("No improvement recommendations available.")

    # --------------------------------------------------------
    # INTERVIEW QUESTIONS
    # --------------------------------------------------------

    st.subheader("AI-Generated Interview Questions")

    questions = result.get("interview_questions", [])
    if questions:
        for i, q in enumerate(questions, start=1):
            st.write(f"{i}. {q}")
    else:
        st.write("No interview questions generated.")

    # --------------------------------------------------------
    # EXTRAS: rewrite + tips (only when client/model supplied)
    # --------------------------------------------------------

    if show_extras and client is not None and model is not None:

        # ---- Resume rewriting ------------------------------------

        with st.expander("✍️ Rewrite My Resume for This Job"):

            st.caption(
                "Generates a tailored summary, improved bullet points, "
                "and a full rewrite. Never invents experience or metrics."
            )

            rewrite_key = f"rewrite_{result.get('resume_name', 'resume')}"

            if st.button(
                "Generate Rewrite",
                key=f"gen_rewrite_{result.get('resume_name', 'resume')}",
            ):
                from resume_rewriter import rewrite_resume

                with st.spinner("Rewriting resume..."):
                    try:
                        rewrite = rewrite_resume(
                            client=client,
                            model=model,
                            resume_text=result.get("resume_text", ""),
                            job_description=result.get(
                                "job_description",
                                st.session_state.get("job_description", ""),
                            ),
                        )
                        st.session_state[rewrite_key] = rewrite
                    except Exception as e:
                        st.error(f"Rewrite failed: {e}")

            rewrite = st.session_state.get(rewrite_key)

            if rewrite:
                from resume_rewriter import build_rewrite_pdf_text

                st.markdown("### Tailored Summary")
                st.write(rewrite.get("tailored_summary", ""))

                st.markdown("### Rewritten Bullets")
                for b in rewrite.get("rewritten_bullets", []):
                    st.write(f"• {b}")

                if rewrite.get("keywords_added"):
                    st.markdown("### JD Keywords Now Surfaced")
                    for k in rewrite["keywords_added"]:
                        st.write(f"- {k}")

                st.markdown("### Full Rewrite")
                st.text_area(
                    "Full rewritten resume",
                    value=rewrite.get("full_rewrite", ""),
                    height=300,
                    key=f"full_rewrite_{result.get('resume_name', 'resume')}",
                )

                st.download_button(
                    label="⬇️ Download Rewrite (TXT)",
                    data=build_rewrite_pdf_text(rewrite).encode("utf-8"),
                    file_name="rewritten_resume.txt",
                    mime="text/plain",
                    key=f"dl_rewrite_{result.get('resume_name', 'resume')}",
                )

        # ---- General tips ----------------------------------------

        with st.expander("Generate General Resume Improvement Tips"):

            if st.button(
                "Generate Tips",
                key=f"gen_tips_{result.get('resume_name', 'resume')}",
            ):
                from llm_analysis import generate_resume_tips

                with st.spinner("Generating recommendations..."):
                    try:
                        tips = generate_resume_tips(
                            client=client,
                            model=model,
                            resume_text=result.get("resume_text", ""),
                        )
                        st.session_state[
                            f"tips_{result.get('resume_name', 'resume')}"
                        ] = tips
                    except Exception as e:
                        st.error(f"Unable to generate tips: {e}")

            tips = st.session_state.get(
                f"tips_{result.get('resume_name', 'resume')}"
            )
            if tips:
                st.write(tips)

    # --------------------------------------------------------
    # PDF DOWNLOAD
    # --------------------------------------------------------

    if show_pdf_download:

        from report_generator import build_pdf_report

        try:
            pdf_bytes = build_pdf_report(result)

            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=(
                    f"resume_report_"
                    f"{result.get('resume_name', 'resume')}.pdf"
                ),
                mime="application/pdf",
                use_container_width=True,
                key=f"pdf_dl_{result.get('resume_name', 'resume')}",
            )
        except Exception as e:
            st.warning(f"Could not generate PDF: {e}")