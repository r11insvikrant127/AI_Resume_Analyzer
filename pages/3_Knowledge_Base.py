import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from page_utils import page_setup
from rag_view import render_knowledge_base
from styles import hero

client, MODEL = page_setup("Knowledge Base", "📖")

hero(
    "Knowledge Base",
    "Ask questions about a company using your own documents.",
    badges=["RAG", "FAISS", "Source Citations"],
)

render_knowledge_base(client, MODEL)