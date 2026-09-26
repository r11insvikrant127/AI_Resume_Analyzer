import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from page_utils import page_setup
from history_view import render_history

client, MODEL = page_setup("History", "📚")

render_history(client, MODEL)