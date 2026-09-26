# page_utils.py

import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from db import init_db
from auth_views import require_login, render_logout_button


def page_setup(page_title, page_icon="📄"):
    """
    Call this at the top of every page. Returns
    (client, MODEL) or halts via st.stop() if not
    authenticated.
    """

    load_dotenv()
    init_db()

    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout="wide",
    )

    # Same CSS as the main app
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .subtitle {
            font-size: 18px;
            color: #666;
            margin-bottom: 25px;
        }
        .formula {
            font-family: monospace;
            background: #f6f6f6;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid #e2e2e2;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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