import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st

from page_utils import page_setup
from admin_dashboard import render_admin_dashboard

client, MODEL = page_setup("Admin", "🛠️")

if not st.session_state.get("is_admin"):
    st.error("Admin access only.")
    st.stop()

render_admin_dashboard()