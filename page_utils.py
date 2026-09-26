# page_utils.py

import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from db import init_db
from auth_views import require_login, render_logout_button
from styles import inject_theme


def page_setup(page_title, page_icon="📄"):
    """
    Bootstrap every page: config, theme, auth, Groq client.
    Returns (client, MODEL).
    """

    load_dotenv()
    init_db()

    st.set_page_config(
        page_title=f"{page_title} · Resume AI",
        page_icon=page_icon,
        layout="wide",
    )

    inject_theme()

    if not require_login():
        st.stop()

    render_logout_button()

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        st.error("GROQ_API_KEY missing in .env")
        st.stop()

    client = Groq(api_key=api_key)
    MODEL = "openai/gpt-oss-120b"

    return client, MODEL