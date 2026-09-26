# auth_views.py

import streamlit as st

from auth import register_user, authenticate


def _set_logged_in(user):
    st.session_state["user_id"] = user.id
    st.session_state["user_email"] = user.email
    st.session_state["user_name"] = user.full_name or user.email
    st.session_state["is_admin"] = bool(user.is_admin)


def _hide_page_nav():
    """
    Hide Streamlit's auto-generated multipage nav while
    the user is logged out. Removes the sidebar entirely
    so no internal page links are visible pre-auth.
    """
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        header[data-testid="stHeader"] { background: transparent; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_login_tab():
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submit = st.form_submit_button("Log in", use_container_width=True, type="primary")

    if submit:
        user = authenticate(email, password)
        if user is None:
            st.error("Invalid email or password.")
        else:
            _set_logged_in(user)
            st.rerun()


def render_signup_tab():
    with st.form("signup_form", clear_on_submit=False):
        full_name = st.text_input("Full name", placeholder="Jane Doe")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="At least 8 characters")
        confirm = st.text_input("Confirm password", type="password", placeholder="Repeat password")
        submit = st.form_submit_button("Create account", use_container_width=True, type="primary")

    if submit:
        if password != confirm:
            st.error("Passwords do not match.")
            return

        user_id, err = register_user(email, password, full_name)

        if err:
            st.error(err)
        else:
            st.success("Account created. Please log in.")


def require_login():
    """
    Return True if authenticated, otherwise render a
    styled login/signup screen and return False.
    """

    if st.session_state.get("user_id"):
        return True

    # ---------- Not logged in ----------
    _hide_page_nav()

    # Inject the shared theme (safe to call again on other pages)
    from styles import inject_theme
    inject_theme()

    # Custom login-page CSS
    st.markdown(
        """
        <style>
        .login-shell {
            max-width: 460px;
            margin: 6vh auto 0 auto;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 36px 32px 28px 32px;
            box-shadow: 0 20px 40px -20px rgba(15, 23, 42, 0.15);
        }
        .login-logo {
            text-align: center;
            font-size: 40px;
            margin-bottom: 4px;
        }
        .login-title {
            text-align: center;
            font-size: 22px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 4px;
        }
        .login-sub {
            text-align: center;
            font-size: 14px;
            color: #64748b;
            margin-bottom: 22px;
        }
        .login-foot {
            text-align: center;
            font-size: 12px;
            color: #94a3b8;
            margin-top: 24px;
        }
        /* Center the tab labels */
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Centered card
    _, mid, _ = st.columns([1, 2, 1])

    with mid:
        st.markdown(
            """
            <div class="login-shell">
                <div class="login-logo">📄</div>
                <div class="login-title">AI Resume Analyzer</div>
                <div class="login-sub">
                    Log in or create an account to continue.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

        with tab_login:
            render_login_tab()

        with tab_signup:
            render_signup_tab()

        st.markdown(
            '<div class="login-foot">'
            'Python · Streamlit · Groq · MySQL · FAISS'
            '</div>',
            unsafe_allow_html=True,
        )

    return False


def render_logout_button():
    with st.sidebar:
        st.divider()

        user_name = st.session_state.get("user_name", "")
        user_name = str(user_name).replace("*", "")

        st.markdown(
            f"Signed in as **{user_name}**"
        )

        if st.button("Log out", use_container_width=True):
            for key in [
                "user_id",
                "user_email",
                "user_name",
                "is_admin",
                "analysis",
                "results",
                "rewrite",
                "recommendations",
            ]:
                st.session_state.pop(key, None)

            st.rerun()