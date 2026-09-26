import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from page_utils import page_setup
from history_view import render_history
from styles import hero

client, MODEL = page_setup("History", "📚")

hero(
    "Resume History",
    "Every analysis you've run, saved and searchable.",
    badges=["Re-open", "Re-run", "Delete"],
)

render_history(client, MODEL)