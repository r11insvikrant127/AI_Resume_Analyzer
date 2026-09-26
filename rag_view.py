# rag_view.py

import streamlit as st

from rag_ingest import list_companies, ingest_company
from rag_query import answer_with_rag
from db_operations import upsert_rag_company, list_rag_companies


def render_knowledge_base(client, model):

    st.header("📖 Knowledge Base (Company / Job Info)")

    st.caption(
        "Drop PDFs and TXTs into data/companies/<company>/ "
        "then click Ingest to build a searchable index."
    )

    # --------------------------------------------------------
    # Ingest
    # --------------------------------------------------------

    st.subheader("1. Ingest Documents")

    companies = list_companies()

    if not companies:
        st.warning(
            "No company folders found. Create "
            "`data/companies/<company>/` and drop PDFs in."
        )
        return

    col1, col2 = st.columns([3, 1])

    with col1:
        company = st.selectbox("Company folder", companies)

    with col2:
        st.write("")
        st.write("")
        if st.button("Ingest", type="primary"):
            with st.spinner(f"Ingesting {company}..."):
                try:
                    docs, chunks = ingest_company(company)
                    upsert_rag_company(company, docs, chunks)
                    st.success(
                        f"Ingested {docs} docs → {chunks} chunks."
                    )
                except Exception as e:
                    st.error(f"Ingest failed: {e}")

    # --------------------------------------------------------
    # Indexed companies
    # --------------------------------------------------------

    indexed = list_rag_companies()

    if indexed:
        st.subheader("2. Indexed Companies")
        st.dataframe(
            [
                {
                    "Company": r.company,
                    "Docs": r.doc_count,
                    "Chunks": r.chunk_count,
                    "Updated": r.updated_at.strftime("%Y-%m-%d %H:%M"),
                }
                for r in indexed
            ],
            use_container_width=True,
        )

    # --------------------------------------------------------
    # Q&A
    # --------------------------------------------------------

    st.subheader("3. Ask a Question")

    all_companies = [r.company for r in indexed] or companies

    ask_company = st.selectbox(
        "Ask about", all_companies, key="rag_ask_company"
    )

    query = st.text_input(
        "Your question",
        placeholder="What does the interview process look like?",
    )

    if st.button("Ask") and query.strip():

        with st.spinner("Searching and answering..."):

            answer, sources = answer_with_rag(
                client, model, ask_company, query
            )

        st.markdown("### Answer")
        st.write(answer)

        if sources:
            with st.expander("Sources"):
                for s in sources:
                    st.write(
                        f"**{s['source']}** (score {s['score']})"
                    )
                    st.caption(s["excerpt"])