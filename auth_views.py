# auth_views.py

import streamlit as st
from auth import register_user, authenticate


def _set_logged_in(user):
    st.session_state["user_id"] = user.id
    st.session_state["user_email"] = user.email
    st.session_state["user_name"] = user.full_name or user.email
    st.session_state["is_admin"] = bool(user.is_admin)


def render_login_tab():
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Log in", use_container_width=True)

    if submit:
        user = authenticate(email, password)
        if user is None:
            st.error("Invalid email or password.")
        else:
            _set_logged_in(user)
            st.success("Logged in.")
            st.rerun()


def render_signup_tab():
    with st.form("signup_form", clear_on_submit=False):
        full_name = st.text_input("Full name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        submit = st.form_submit_button("Create account", use_container_width=True)

    if submit:
        if password != confirm:
            st.error("Passwords do not match.")
            return

        user_id, err = register_user(email, password, full_name)

        if err:
            st.error(err)
        else:
            st.success("Account created. Please log in.")
            st.rerun()


def require_login():
    """
    Return True if authenticated, otherwise render the
    login/signup UI and return False.

    Call this near the top of app.py, after page config.
    """

    if st.session_state.get("user_id"):
        return True

    st.markdown(
        '<div class="main-title">AI Resume Analyzer</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtitle">Log in or create an account to continue.</div>',
        unsafe_allow_html=True,
    )

    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        render_login_tab()

    with tab_signup:
        render_signup_tab()

    return False


def render_logout_button():
    with st.sidebar:
        st.divider()
        st.write(f"Signed in as **{st.session_state.get('user_name', '')}**")
        if st.button("Log out", use_container_width=True):
            for key in ["user_id", "user_email", "user_name", "is_admin",
                        "analysis", "results", "rewrite", "recommendations"]:
                st.session_state.pop(key, None)
            st.rerun()