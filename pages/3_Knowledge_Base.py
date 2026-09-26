import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from page_utils import page_setup
from rag_view import render_knowledge_base

client, MODEL = page_setup("Knowledge Base", "📖")

render_knowledge_base(client, MODEL)