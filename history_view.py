# history_view.py

import json
import streamlit as st

from db_operations import (
    list_user_analyses_with_pagination,
    count_user_analyses,
    delete_analysis,
    get_analysis_by_id,
)
from report_view import render_single_report


PAGE_SIZE = 10


def render_history(client, model):
    """
    Full resume history view for the logged-in user.
    """

    st.header("📚 Resume History")
    st.caption(
        "Every analysis you've run is stored here. "
        "Re-open, re-run, or delete past analyses."
    )

    user_id = st.session_state["user_id"]

    # --------------------------------------------------------
    # Session-state for the currently opened analysis
    # --------------------------------------------------------

    if "history_open_id" not in st.session_state:
        st.session_state["history_open_id"] = None

    # --------------------------------------------------------
    # Opened analysis view (takes priority over list)
    # --------------------------------------------------------

    if st.session_state["history_open_id"] is not None:

        opened = get_analysis_by_id(
            st.session_state["history_open_id"],
            user_id=user_id,
        )

        if not opened:
            st.warning("Analysis not found.")
            st.session_state["history_open_id"] = None
            st.rerun()

        if st.button("⬅️ Back to list"):
            st.session_state["history_open_id"] = None
            st.rerun()

        st.subheader(f"Re-opened: {opened.resume_name}")
        st.caption(
            f"Analysis #{opened.id} · "
            f"{opened.created_at.strftime('%Y-%m-%d %H:%M')}"
        )

        render_single_report(
            opened.result_json,
            client=client,
            model=model,
            show_pdf_download=True,
            show_extras=False,
        )

        st.divider()
        st.subheader("Job Description (as used)")
        st.text_area(
            "JD",
            value=opened.jd_text,
            height=200,
            disabled=True,
            key=f"history_jd_{opened.id}",
        )

        # ------------------------------------------------
        # Re-run this JD with a fresh upload
        # ------------------------------------------------

        st.divider()
        st.subheader("🔁 Re-run this Analysis")

        with st.form(f"rerun_form_{opened.id}"):

            rerun_file = st.file_uploader(
                "Upload a resume to compare against the same JD",
                type=["pdf", "docx"],
            )
            rerun_submit = st.form_submit_button(
                "Re-run",
                use_container_width=True,
            )

        if rerun_submit and rerun_file:

            from analysis_pipeline import analyze_single_resume
            from keyword_analyzer import extract_keywords_from_jd
            from llm_analysis import analyze_resume
            from db_operations import save_resume, save_analysis
            import hashlib

            with st.spinner("Re-running analysis..."):

                try:
                    # Use the saved JD text — same input as before
                    req_data = extract_keywords_from_jd(
                        client, model, opened.jd_text
                    )

                    result = analyze_single_resume(
                        uploaded_file=rerun_file,
                        job_description=opened.jd_text,
                        requirement_data=req_data,
                        analyze_resume_llm=lambda t, j: analyze_resume(
                            client, model, t, j
                        ),
                        client=client,
                        model=model,
                    )

                    # Persist the new analysis
                    try:
                        resume_id = save_resume(
                            user_id=user_id,
                            filename=rerun_file.name,
                            file_hash=hashlib.sha256(
                                result["resume_text"].encode("utf-8")
                            ).hexdigest(),
                            raw_text=result["resume_text"],
                        )
                        save_analysis(
                            user_id=user_id,
                            resume_id=resume_id,
                            resume_name=result["resume_name"],
                            jd_text=opened.jd_text,
                            result=result,
                        )
                    except Exception as db_err:
                        st.warning(f"Saved to UI but not DB: {db_err}")

                    st.success(
                        f"New analysis for {result['resume_name']} "
                        f"saved to history."
                    )

                except Exception as e:
                    st.error(f"Re-run failed: {e}")

        return

    # --------------------------------------------------------
    # List view
    # --------------------------------------------------------

    total = count_user_analyses(user_id)

    if total == 0:
        st.info(
            "No analyses yet. Go to the Analyzer page "
            "and run one to see it appear here."
        )
        return

    # Pagination state
    if "history_page" not in st.session_state:
        st.session_state["history_page"] = 0

    page = st.session_state["history_page"]
    offset = page * PAGE_SIZE

    rows = list_user_analyses_with_pagination(
        user_id, offset=offset, limit=PAGE_SIZE
    )

    st.write(f"**{total} analyses total** · "
             f"Page {page + 1} of {max(1, (total - 1) // PAGE_SIZE + 1)}")

    # --------------------------------------------------------
    # Table
    # --------------------------------------------------------

    for row in rows:

        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 2])

        with col1:
            st.markdown(f"**{row.resume_name}**")
            st.caption(
                f"#{row.id} · "
                f"{row.created_at.strftime('%Y-%m-%d %H:%M')}"
            )

        with col2:
            st.metric("ATS", f"{row.ats_score:.0f}%")

        with col3:
            st.metric("Req", f"{row.required_match_percentage:.0f}%")

        with col4:
            st.metric("Tech", f"{row.technical_skill_percentage:.0f}%")

        with col5:
            b1, b2, b3 = st.columns(3)

            with b1:
                if st.button("Open", key=f"open_{row.id}"):
                    st.session_state["history_open_id"] = row.id
                    st.rerun()

            with b2:
                if st.button("Re-run JD", key=f"rerun_btn_{row.id}"):
                    st.session_state["history_open_id"] = row.id
                    st.rerun()

            with b3:
                if st.button("Delete", key=f"del_{row.id}"):
                    if delete_analysis(row.id, user_id):
                        st.success(f"Deleted #{row.id}")
                        st.rerun()
                    else:
                        st.error("Delete failed.")

        st.divider()

    # --------------------------------------------------------
    # Pagination controls
    # --------------------------------------------------------

    pc1, pc2, pc3 = st.columns([1, 3, 1])

    with pc1:
        if page > 0 and st.button("⬅️ Previous"):
            st.session_state["history_page"] = page - 1
            st.rerun()

    with pc3:
        max_page = max(0, (total - 1) // PAGE_SIZE)
        if page < max_page and st.button("Next ➡️"):
            st.session_state["history_page"] = page + 1
            st.rerun()