# rag_query.py

from rag_store import search


RAG_SYSTEM = (
    "You are an assistant answering questions about a company "
    "and its hiring process. Use ONLY the provided context "
    "excerpts. If the answer is not in the context, say you "
    "don't have that information in the knowledge base. "
    "Cite sources by filename in brackets, e.g. [handbook.pdf]."
)


def answer_with_rag(client, model, company, query, top_k=5):
    """
    Returns (answer_text, sources_list).
    """

    hits = search(company, query, top_k=top_k)

    if not hits:
        return (
            "No knowledge base is indexed for this company yet. "
            "Upload documents first.",
            [],
        )

    context_blocks = []
    sources = []

    for i, h in enumerate(hits, start=1):
        src = h["metadata"].get("source", "unknown")
        sources.append({
            "source": src,
            "score": round(h["score"], 3),
            "excerpt": h["text"][:200] + ("..." if len(h["text"]) > 200 else ""),
        })
        context_blocks.append(
            f"[{i}] source={src}\n{h['text']}"
        )

    context = "\n\n".join(context_blocks)

    prompt = f"""
COMPANY: {company}

CONTEXT EXCERPTS:

{context}

USER QUESTION:

{query}

Answer using ONLY the context above.
Cite sources in brackets.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": RAG_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content or "", sources