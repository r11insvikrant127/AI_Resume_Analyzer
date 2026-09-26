import base64
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image

from auth import register_user, authenticate


BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "assets" / "resume_ai_icon.png"


# ============================================================
# USER SESSION
# ============================================================

def _set_logged_in(user):
    st.session_state["user_id"] = user.id
    st.session_state["user_email"] = user.email

    clean_name = str(user.full_name or user.email)
    clean_name = clean_name.replace("*", "").strip()

    st.session_state["user_name"] = clean_name
    st.session_state["is_admin"] = bool(user.is_admin)


# ============================================================
# PAGE CLEANUP
# ============================================================

def _hide_page_nav():
    st.html("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }

        [data-testid="collapsedControl"] {
            display: none !important;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        [data-testid="stToolbar"] {
            display: none !important;
        }

        #MainMenu {
            display: none !important;
        }

        footer {
            display: none !important;
        }
    </style>
    """)


# ============================================================
# TRANSPARENT LOGO
# ============================================================

@st.cache_data
def _transparent_logo_base64():
    """
    Removes only the white background connected to the
    outside edges of the PNG.

    This preserves the white parts INSIDE the actual
    resume illustration.
    """

    if not ICON_PATH.exists():
        return None

    image = Image.open(ICON_PATH).convert("RGBA")

    pixels = image.load()
    width, height = image.size

    # Pixels considered background-white
    def is_background(pixel):
        r, g, b, a = pixel
        return (
            a > 0
            and r >= 242
            and g >= 242
            and b >= 242
        )

    # Flood-fill only white pixels connected to image edges.
    visited = set()
    stack = []

    for x in range(width):
        stack.append((x, 0))
        stack.append((x, height - 1))

    for y in range(height):
        stack.append((0, y))
        stack.append((width - 1, y))

    while stack:

        x, y = stack.pop()

        if (x, y) in visited:
            continue

        if x < 0 or x >= width or y < 0 or y >= height:
            continue

        visited.add((x, y))

        if not is_background(pixels[x, y]):
            continue

        # Make background transparent
        r, g, b, a = pixels[x, y]
        pixels[x, y] = (r, g, b, 0)

        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))

    output = BytesIO()
    image.save(output, format="PNG")

    return base64.b64encode(output.getvalue()).decode("utf-8")


def _render_logo():
    logo = _transparent_logo_base64()

    if not logo:
        st.html("""
        <div class="auth-fallback-icon">📄</div>
        """)
        return

    st.html(
        f"""
        <div class="auth-logo-wrapper">
            <img
                class="auth-logo"
                src="data:image/png;base64,{logo}"
                alt="AI Resume Analyzer"
            />
        </div>
        """
    )


# ============================================================
# LOGIN
# ============================================================

def render_login_tab():

    with st.form(
        "login_form",
        clear_on_submit=False,
        border=False
    ):

        email = st.text_input(
            "Email address",
            placeholder="you@example.com",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )

        submit = st.form_submit_button(
            "Log in",
            width="stretch",
            type="primary",
            icon=":material/login:"
        )

    if submit:

        if not email.strip() or not password:
            st.warning(
                "Please enter your email and password."
            )
            return

        user = authenticate(
            email.strip(),
            password
        )

        if user is None:
            st.error("Invalid email or password.")

        else:
            _set_logged_in(user)
            st.rerun()


# ============================================================
# SIGN UP
# ============================================================

def render_signup_tab():

    with st.form(
        "signup_form",
        clear_on_submit=False,
        border=False
    ):

        full_name = st.text_input(
            "Full name",
            placeholder="Jane Doe",
            key="signup_name"
        )

        email = st.text_input(
            "Email address",
            placeholder="you@example.com",
            key="signup_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="At least 8 characters",
            key="signup_password"
        )

        confirm = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Repeat your password",
            key="signup_confirm"
        )

        submit = st.form_submit_button(
            "Create account",
            width="stretch",
            type="primary",
            icon=":material/person_add:"
        )

    if submit:

        if not full_name.strip():
            st.warning("Please enter your full name.")
            return

        if not email.strip():
            st.warning("Please enter your email address.")
            return

        if len(password) < 8:
            st.warning(
                "Password must contain at least 8 characters."
            )
            return

        if password != confirm:
            st.error("Passwords do not match.")
            return

        user_id, err = register_user(
            email.strip(),
            password,
            full_name.strip()
        )

        if err:
            st.error(err)

        else:
            st.success(
                "Account created successfully. You can now log in."
            )


# ============================================================
# CUSTOM LOGIN / SIGNUP TABS
# ============================================================

def _render_auth_tabs():

    if "auth_tab" not in st.session_state:
        st.session_state["auth_tab"] = "login"

    login_col, signup_col = st.columns(
        2,
        gap="small"
    )

    # --------------------------------------------------------
    # LOGIN TAB
    # --------------------------------------------------------

    with login_col:

        st.html("""
        <div class="auth-tab-icon auth-login-icon">
            ↪
        </div>
        """)

        if st.button(
            "Log in",
            key="auth_login_tab",
            width="stretch"
        ):
            st.session_state["auth_tab"] = "login"
            st.rerun()

    # --------------------------------------------------------
    # SIGNUP TAB
    # --------------------------------------------------------

    with signup_col:

        st.html("""
        <div class="auth-tab-icon auth-signup-icon">
            ♟
        </div>
        """)

        if st.button(
            "Create account",
            key="auth_signup_tab",
            width="stretch"
        ):
            st.session_state["auth_tab"] = "signup"
            st.rerun()

    # --------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------

    st.html("""
    <div class="auth-tab-divider"></div>
    """)

    if st.session_state["auth_tab"] == "login":

        st.html("""
        <div class="auth-tab-description">
            Welcome back. Sign in to continue.
        </div>
        """)

        render_login_tab()

    else:

        st.html("""
        <div class="auth-tab-description">
            Create your account and start analyzing resumes.
        </div>
        """)

        render_signup_tab()


# ============================================================
# BACKGROUND
# ============================================================

def _render_auth_background():

    st.html("""
    <div class="auth-background">

        <div class="auth-center-glow"></div>

        <!-- TOP WAVES -->
        <div class="auth-top-ribbon auth-top-ribbon-left"></div>
        <div class="auth-top-ribbon auth-top-ribbon-right"></div>

        <!-- BOTTOM WAVES -->
        <div class="auth-bottom-ribbon auth-bottom-ribbon-left"></div>
        <div class="auth-bottom-ribbon auth-bottom-ribbon-right"></div>

        <!-- EXTRA CURVES -->
        <div class="auth-ribbon-line auth-ribbon-line-left"></div>
        <div class="auth-ribbon-line auth-ribbon-line-right"></div>

        <!-- GRID -->
        <div class="auth-grid auth-grid-left"></div>
        <div class="auth-grid auth-grid-right"></div>

        <!-- DOTS -->
        <div class="auth-dots auth-dots-left"></div>
        <div class="auth-dots auth-dots-right"></div>

        <!-- FLOATING CARDS -->
        <div class="floating-card floating-card-doc">
            <span>▤</span>
        </div>

        <div class="floating-card floating-card-job">
            <span>▣</span>
        </div>

        <div class="floating-card floating-card-chart">
            <span>▥</span>
        </div>

        <div class="floating-card floating-card-study">
            <span>◆</span>
        </div>

        <!-- ORBS -->
        <div class="auth-orb auth-orb-1"></div>
        <div class="auth-orb auth-orb-2"></div>
        <div class="auth-orb auth-orb-3"></div>
        <div class="auth-orb auth-orb-4"></div>
        <div class="auth-orb auth-orb-5"></div>

    </div>
    """)


# ============================================================
# MAIN LOGIN PAGE
# ============================================================

def require_login():

    if st.session_state.get("user_id"):
        return True

    _hide_page_nav()

    from styles import inject_theme
    inject_theme()

    _render_auth_background()

    # --------------------------------------------------------
    # TOP SPACING
    # --------------------------------------------------------

    st.html("""
    <div class="auth-page-spacer"></div>
    """)

    # --------------------------------------------------------
    # FIXED 680px CENTER CONTAINER
    # --------------------------------------------------------

    with st.container(
        width=680,
        horizontal_alignment="center",
        gap="small"
    ):

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        _render_logo()

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        st.html("""
        <div class="auth-heading">

            <div class="auth-title">
                AI Resume <span>Analyzer</span>
            </div>

            <div class="auth-subtitle">
                Analyze your resume. Match the right jobs.<br>
                Build a stronger career profile.
            </div>

        </div>
        """)

        # ----------------------------------------------------
        # LOGIN CARD
        # ----------------------------------------------------

        with st.container(
            key="auth-card",
            width=560,
            border=False,
            gap="small"
        ):

            _render_auth_tabs()

        # ----------------------------------------------------
        # TRUST ROW
        # ----------------------------------------------------

        st.html("""
        <div class="auth-tech-row">

            <span class="auth-tech">
                <span class="auth-tech-icon">⚡</span>
                AI-powered
            </span>

            <span class="auth-tech-separator">|</span>

            <span class="auth-tech">
                <span class="auth-tech-icon">🔐</span>
                Secure
            </span>

            <span class="auth-tech-separator">|</span>

            <span class="auth-tech">
                <span class="auth-tech-icon">🎯</span>
                Job matching
            </span>

        </div>
        """)

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        st.html("""
        <div class="auth-footer">

            <div class="auth-footer-title">
                AI Resume Analyzer
            </div>

            <div class="auth-footer-stack">
                Python · Streamlit · Groq · MySQL · FAISS
            </div>

            <div class="auth-footer-note">
                Your resume. Your data. Your career.
            </div>

        </div>
        """)

    return False


# ============================================================
# LOGOUT
# ============================================================

def render_logout_button():

    with st.sidebar:

        st.divider()

        user_name = str(
            st.session_state.get(
                "user_name",
                ""
            )
        ).replace("*", "").strip()

        st.html(
            f"""
            <div class="sidebar-user-card">

                <div class="sidebar-user-label">
                    SIGNED IN AS
                </div>

                <div class="sidebar-user-name">
                    {user_name}
                </div>

            </div>
            """
        )

        if st.button(
            "Log out",
            width="stretch",
            icon=":material/logout:"
        ):

            for key in [
                "user_id",
                "user_email",
                "user_name",
                "is_admin",
                "analysis",
                "results",
                "rewrite",
                "recommendations"
            ]:
                st.session_state.pop(
                    key,
                    None
                )

            st.rerun()