# page_utils.py

import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from db import init_db_cached
from auth_views import require_login, render_logout_button
from styles import inject_theme, loading_bar


def page_setup(page_title, page_icon="📄"):
    """
    Bootstrap every page: config, theme, auth, Groq client.

    Cached resources (DB init, Groq client) only run once per
    Streamlit process, so switching between pages is fast.
    """

    # --------------------------------------------------------
    # Streamlit page config — must be the very first st.* call
    # --------------------------------------------------------

    st.set_page_config(
        page_title=f"{page_title} · Resume AI",
        page_icon=page_icon,
        layout="wide",
    )

    # --------------------------------------------------------
    # Immediate visual feedback while the rest of the page loads
    # --------------------------------------------------------

    bar = loading_bar()

    # --------------------------------------------------------
    # Environment + DB (cached)
    # --------------------------------------------------------

    load_dotenv()
    init_db_cached()

    # --------------------------------------------------------
    # Theme (guarded — runs once per session)
    # --------------------------------------------------------

    inject_theme()

    # --------------------------------------------------------
    # Auth gate
    # --------------------------------------------------------

    if not require_login():
        bar.empty()
        st.stop()

    render_logout_button()

    # --------------------------------------------------------
    # Groq client (cached per API key)
    # --------------------------------------------------------

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        bar.empty()
        st.error("GROQ_API_KEY missing in .env")
        st.stop()

    @st.cache_resource(show_spinner=False)
    def _make_client(key):
        return Groq(api_key=key)

    client = _make_client(api_key)
    MODEL = "openai/gpt-oss-120b"

    # --------------------------------------------------------
    # Done loading
    # --------------------------------------------------------

    bar.empty()

    return client, MODEL