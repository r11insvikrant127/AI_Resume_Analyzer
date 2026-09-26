import streamlit as st


def inject_theme():
    """
    Global application theme + authentication page styling.
    """

    st.html(
        """
        <style>

        /* =========================================================
           GLOBAL
           ========================================================= */

        :root {
            --primary-blue: #2563eb;
            --primary-indigo: #4f46e5;

            --text-dark: #172554;
            --text-main: #334155;
            --text-muted: #71819d;
            --text-light: #94a3b8;

            --border-light: #e4e8ef;

            --input-bg: #f3f5f8;

            --white: #ffffff;
        }


        /* =========================================================
           STREAMLIT APP
           ========================================================= */

        .stApp {

            min-height: 100vh;

            background:
                radial-gradient(
                    circle at 50% 34%,
                    rgba(255, 255, 255, 0.98) 0%,
                    rgba(248, 251, 255, 0.96) 25%,
                    rgba(239, 246, 255, 0.92) 55%,
                    rgba(231, 240, 255, 0.88) 100%
                );

            color: var(--text-main);
        }


        /* Remove Streamlit top whitespace */

        .block-container {

            padding-top: 0.4rem !important;
            padding-bottom: 1rem !important;

            width: 100% !important;
            max-width: 100% !important;

            margin-left: auto !important;
            margin-right: auto !important;
        }


        /* =========================================================
           AUTH PAGE BACKGROUND
           ========================================================= */

        .auth-background {

            position: fixed;

            inset: 0;

            width: 100vw;
            height: 100vh;

            overflow: hidden;

            pointer-events: none;

            z-index: 0;

            background:
                radial-gradient(
                    ellipse at center,
                    rgba(255,255,255,0.98) 0%,
                    rgba(248,251,255,0.90) 42%,
                    rgba(238,246,255,0.72) 75%,
                    rgba(229,239,255,0.62) 100%
                );
        }


        /* =========================================================
           CENTER WHITE GLOW
           ========================================================= */

        .auth-center-glow {

            position: absolute;

            width: 950px;
            height: 650px;

            left: 50%;
            top: 47%;

            transform: translate(-50%, -50%);

            border-radius: 50%;

            background:
                radial-gradient(
                    ellipse,
                    rgba(255,255,255,0.96) 0%,
                    rgba(255,255,255,0.72) 38%,
                    rgba(255,255,255,0.18) 70%,
                    transparent 100%
                );

            filter: blur(5px);
        }


        /* =========================================================
           TOP LEFT RIBBON
           ========================================================= */

        .auth-top-ribbon {

            position: absolute;

            width: 1100px;
            height: 470px;

            top: -385px;

            border-radius: 50%;

            background:
                linear-gradient(
                    135deg,
                    rgba(181,210,255,0.68),
                    rgba(225,235,255,0.20)
                );

            box-shadow:
                inset 0 -65px 0
                rgba(255,255,255,0.42);
        }

        .auth-top-ribbon-left {

            left: -500px;

            transform: rotate(-10deg);
        }


        /* =========================================================
           TOP RIGHT RIBBON
           ========================================================= */

        .auth-top-ribbon-right {

            right: -500px;

            transform: rotate(10deg);
        }


        /* =========================================================
           BOTTOM LEFT RIBBON
           ========================================================= */

        .auth-bottom-ribbon {

            position: absolute;

            width: 1100px;
            height: 600px;

            bottom: -470px;

            border-radius: 50%;

            background:
                linear-gradient(
                    145deg,
                    rgba(104,155,255,0.42),
                    rgba(129,140,248,0.10)
                );

            border-top:
                68px solid
                rgba(255,255,255,0.75);

            box-shadow:
                inset 0 35px 45px
                rgba(255,255,255,0.18);
        }

        .auth-bottom-ribbon-left {

            left: -500px;

            transform: rotate(-10deg);
        }


        /* =========================================================
           BOTTOM RIGHT RIBBON
           ========================================================= */

        .auth-bottom-ribbon-right {

            right: -500px;

            transform: rotate(10deg);
        }


        /* =========================================================
           EXTRA CURVED WHITE LINES
           ========================================================= */

        .auth-ribbon-line {

            position: absolute;

            width: 800px;
            height: 380px;

            border-radius: 50%;

            border: 1px solid
                rgba(255,255,255,0.78);

            opacity: 0.85;
        }


        .auth-ribbon-line-left {

            left: -410px;
            bottom: -255px;

            transform: rotate(-13deg);
        }


        .auth-ribbon-line-right {

            right: -410px;
            bottom: -255px;

            transform: rotate(13deg);
        }


        /* =========================================================
           GRID DECORATION
           ========================================================= */

        .auth-grid {

            position: absolute;

            width: 150px;
            height: 110px;

            opacity: 0.35;

            background-image:
                linear-gradient(
                    rgba(107,140,255,0.13) 1px,
                    transparent 1px
                ),
                linear-gradient(
                    90deg,
                    rgba(107,140,255,0.13) 1px,
                    transparent 1px
                );

            background-size: 18px 18px;
        }


        .auth-grid-left {

            left: 10px;
            top: 160px;
        }


        .auth-grid-right {

            right: 10px;
            top: 160px;
        }


        /* =========================================================
           DOT GRIDS
           ========================================================= */

        .auth-dots {

            position: absolute;

            width: 90px;
            height: 90px;

            opacity: 0.60;

            background-image:
                radial-gradient(
                    circle,
                    rgba(99,102,241,0.48) 2px,
                    transparent 2px
                );

            background-size: 14px 14px;
        }


        .auth-dots-left {

            left: 285px;
            bottom: 230px;
        }


        .auth-dots-right {

            right: 190px;
            top: 195px;
        }


        /* =========================================================
           FLOATING CARDS
           ========================================================= */

        .floating-card {

            position: absolute;

            width: 46px;
            height: 46px;

            display: flex;

            align-items: center;
            justify-content: center;

            border-radius: 11px;

            background:
                rgba(255,255,255,0.90);

            border:
                1px solid
                rgba(255,255,255,0.95);

            box-shadow:
                0 12px 28px
                rgba(75,105,170,0.13);

            backdrop-filter: blur(12px);

            -webkit-backdrop-filter: blur(12px);

            color: #667eea;

            font-size: 17px;

            z-index: 2;
        }


        .floating-card-doc {

            left: 220px;
            top: 210px;

            transform: rotate(-6deg);
        }


        .floating-card-job {

            right: 205px;
            top: 198px;

            transform: rotate(5deg);
        }


        .floating-card-chart {

            left: 205px;
            top: 450px;

            transform: rotate(-7deg);
        }


        .floating-card-study {

            right: 205px;
            top: 475px;

            transform: rotate(6deg);
        }


        /* =========================================================
           SMALL GLOWING ORBS
           ========================================================= */

        .auth-orb {

            position: absolute;

            border-radius: 50%;

            background:
                rgba(96,165,250,0.36);

            box-shadow:
                0 0 20px
                rgba(96,165,250,0.12);
        }


        .auth-orb-1 {

            width: 12px;
            height: 12px;

            left: 30.5%;
            top: 11%;
        }


        .auth-orb-2 {

            width: 10px;
            height: 10px;

            right: 20.5%;
            top: 13%;
        }


        .auth-orb-3 {

            width: 9px;
            height: 9px;

            left: 21.5%;
            bottom: 17%;
        }


        .auth-orb-4 {

            width: 17px;
            height: 17px;

            right: 25%;
            bottom: 18%;
        }


        .auth-orb-5 {

            width: 8px;
            height: 8px;

            left: 36%;
            bottom: 25%;
        }


        /* =========================================================
           TOP SPACING
           ========================================================= */

        .auth-page-spacer {

            height: 24px;
        }

        /* =========================================================
        CENTER ENTIRE AUTH SHELL
        ========================================================= */

        .st-key-auth-shell {

            width: 680px !important;
            max-width: 680px !important;

            margin-left: auto !important;
            margin-right: auto !important;

            position: relative;

            z-index: 10;
        }

        /* =========================================================
           LOGO
           ========================================================= */

        .auth-logo-wrapper {

            width: 100%;

            height: 145px;

            display: flex;

            align-items: center;

            justify-content: center;

            margin: 0 auto;

            padding: 0;

            position: relative;

            z-index: 10;
        }


        .auth-logo {

            width: 145px;

            height: 145px;

            object-fit: contain;

            display: block;

            background: transparent !important;

            border: none !important;

            border-radius: 0 !important;

            box-shadow: none !important;

            outline: none !important;
        }


        /* =========================================================
           FALLBACK LOGO
           ========================================================= */

        .auth-fallback-icon {

            width: 145px;
            height: 145px;

            margin: 0 auto;

            display: flex;

            align-items: center;
            justify-content: center;

            font-size: 68px;
        }


        /* =========================================================
           TITLE
           ========================================================= */

        .auth-heading {

            width: 100%;

            text-align: center;

            margin-top: -3px;

            margin-bottom: 20px;

            position: relative;

            z-index: 10;
        }


        .auth-title {

            font-family:
                "Inter",
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            font-size: 30px;

            line-height: 1.15;

            font-weight: 800;

            letter-spacing: -1.1px;

            color: #172554;

            margin: 0;
        }


        .auth-title span {

            background:
                linear-gradient(
                    90deg,
                    #2563eb,
                    #4f46e5
                );

            -webkit-background-clip: text;

            -webkit-text-fill-color: transparent;

            background-clip: text;
        }


        .auth-subtitle {

            margin-top: 8px;

            font-size: 11px;

            line-height: 1.55;

            color: #71819d;

            font-weight: 400;
        }


        /* =========================================================
           AUTH CARD
           ========================================================= */

        .st-key-auth-card {

            width: 560px !important;

            max-width: 560px !important;

            margin-left: auto !important;

            margin-right: auto !important;

            padding:
                12px
                20px
                18px
                20px !important;

            background:
                rgba(
                    255,
                    255,
                    255,
                    0.88
                ) !important;

            border:
                1px solid
                rgba(
                    255,
                    255,
                    255,
                    0.95
                ) !important;

            border-radius: 16px !important;

            box-shadow:
                0 20px 48px
                rgba(
                    46,
                    70,
                    125,
                    0.13
                ),
                0 5px 16px
                rgba(
                    70,
                    100,
                    170,
                    0.07
                ) !important;

            backdrop-filter: blur(18px);

            -webkit-backdrop-filter: blur(18px);

            position: relative;

            z-index: 20;
        }


        /* =========================================================
           TAB COLUMNS
           ========================================================= */

        .st-key-auth-card
        [data-testid="stHorizontalBlock"] {

            width: 100% !important;

            gap: 0 !important;

            margin: 0 !important;
        }


        .st-key-auth-card
        [data-testid="column"] {

            padding:
                0
                0.2rem !important;

            display: flex;

            flex-direction: column;

            align-items: center;
        }


        /* =========================================================
           TAB ICONS
           ========================================================= */

        .auth-tab-icon {

            width: 100%;

            height: 27px;

            display: flex;

            align-items: center;

            justify-content: center;

            text-align: center;

            font-size: 21px;

            line-height: 1;

            font-weight: 700;

            margin: 0;

            padding: 0;
        }


        .auth-login-icon {

            color: #2563eb;
        }


        .auth-signup-icon {

            color: #64748b;
        }


        /* =========================================================
           TAB BUTTONS
           ========================================================= */

        .st-key-auth_login_tab button,
        .st-key-auth_signup_tab button {

            width: 100% !important;

            height: 34px !important;

            min-height: 34px !important;

            padding: 0 !important;

            margin: 0 !important;

            border: none !important;

            border-radius: 0 !important;

            background: transparent !important;

            box-shadow: none !important;

            color: #667085 !important;

            font-size: 12px !important;

            font-weight: 600 !important;

            text-align: center !important;

            justify-content: center !important;

            align-items: center !important;

            transition:
                color 0.18s ease,
                background 0.18s ease;
        }


        .st-key-auth_login_tab button:hover,
        .st-key-auth_signup_tab button:hover {

            color: #2563eb !important;

            background:
                rgba(
                    37,
                    99,
                    235,
                    0.025
                ) !important;
        }


        .st-key-auth_login_tab button {

            color: #2563eb !important;

            font-weight: 700 !important;
        }


        /* =========================================================
           TAB DIVIDER
           ========================================================= */

        .auth-tab-divider {

            width: 100%;

            height: 1px;

            background: #e4e8ef;

            margin-top: -2px;

            margin-bottom: 15px;

            position: relative;
        }


        .auth-tab-divider::before {

            content: "";

            position: absolute;

            left: 0;

            top: -1px;

            width: 50%;

            height: 2px;

            background:
                linear-gradient(
                    90deg,
                    #2563eb,
                    #4f46e5
                );

            border-radius: 2px;
        }


        /* =========================================================
           DESCRIPTION
           ========================================================= */

        .auth-tab-description {

            text-align: center;

            color: #71819d;

            font-size: 10px;

            line-height: 1.4;

            margin-bottom: 19px;
        }


        /* =========================================================
           FORM LABELS
           ========================================================= */

        .st-key-auth-card label {

            color: #334155 !important;

            font-size: 11px !important;

            font-weight: 600 !important;
        }


        /* =========================================================
           INPUT FIELDS
           ========================================================= */

        .st-key-auth-card input {

            height: 34px !important;

            min-height: 34px !important;

            border-radius: 7px !important;

            border:
                1px solid
                #e1e6ee !important;

            background:
                #f3f5f8 !important;

            color: #334155 !important;

            font-size: 11px !important;

            box-shadow: none !important;
        }


        .st-key-auth-card input::placeholder {

            color: #a8b5c9 !important;

            opacity: 1 !important;
        }


        .st-key-auth-card input:focus {

            border-color:
                #4f46e5 !important;

            box-shadow:
                0 0 0 2px
                rgba(
                    79,
                    70,
                    229,
                    0.10
                ) !important;
        }


        /* =========================================================
           PRIMARY BUTTON
           ========================================================= */

        .st-key-auth-card
        button[kind="primary"] {

            height: 34px !important;

            min-height: 34px !important;

            border: none !important;

            border-radius: 7px !important;

            background:
                linear-gradient(
                    90deg,
                    #2563eb,
                    #4f46e5
                ) !important;

            box-shadow:
                0 7px 18px
                rgba(
                    59,
                    91,
                    220,
                    0.24
                ) !important;

            font-size: 11px !important;

            font-weight: 700 !important;

            color: white !important;
        }


        .st-key-auth-card
        button[kind="primary"]:hover {

            background:
                linear-gradient(
                    90deg,
                    #1d4ed8,
                    #4338ca
                ) !important;

            box-shadow:
                0 8px 20px
                rgba(
                    59,
                    91,
                    220,
                    0.30
                ) !important;
        }


        /* =========================================================
           FORM SPACING
           ========================================================= */

        .st-key-auth-card
        [data-testid="stForm"] {

            border: none !important;

            padding: 0 !important;

            background: transparent !important;
        }


        .st-key-auth-card
        [data-testid="stFormSubmitButton"] {

            margin-top: 4px !important;
        }


        /* =========================================================
           WARNING / ERROR / SUCCESS
           ========================================================= */

        .st-key-auth-card
        [data-testid="stAlert"] {

            font-size: 10px !important;

            border-radius: 7px !important;
        }


        /* =========================================================
           TRUST ROW
           ========================================================= */

        .auth-tech-row {

            width: 560px;

            max-width: 100%;

            margin:
                17px
                auto
                0
                auto;

            display: flex;

            justify-content: center;

            align-items: center;

            gap: 12px;

            color: #71819d;

            font-size: 9px;

            text-align: center;

            position: relative;

            z-index: 10;
        }


        .auth-tech {

            display: inline-flex;

            align-items: center;

            justify-content: center;

            gap: 4px;

            white-space: nowrap;
        }


        .auth-tech-icon {

            font-size: 10px;
        }


        .auth-tech-separator {

            color: #c7cfdb;
        }


        /* =========================================================
           FOOTER
           ========================================================= */

        .auth-footer {

            width: 560px;

            max-width: 100%;

            margin:
                18px
                auto
                0
                auto;

            padding-top: 11px;

            border-top:
                1px solid
                rgba(
                    148,
                    163,
                    184,
                    0.22
                );

            text-align: center;

            position: relative;

            z-index: 10;

            color: #94a3b8;
        }


        .auth-footer-title {

            color: #475569;

            font-size: 9px;

            font-weight: 700;

            margin-bottom: 4px;
        }


        .auth-footer-stack {

            font-size: 8px;

            color: #94a3b8;

            margin-bottom: 4px;
        }


        .auth-footer-note {

            font-size: 8px;

            color: #c0c8d4;
        }


        /* =========================================================
           SIDEBAR
           ========================================================= */

        [data-testid="stSidebar"] {

            background:
                linear-gradient(
                    180deg,
                    #f8faff,
                    #eef4ff
                ) !important;

            border-right:
                1px solid
                rgba(
                    148,
                    163,
                    184,
                    0.14
                ) !important;
        }


        .sidebar-user-card {

            width: 100%;

            padding:
                11px
                12px;

            margin-bottom: 8px;

            border-radius: 10px;

            background:
                rgba(
                    255,
                    255,
                    255,
                    0.72
                );

            border:
                1px solid
                rgba(
                    148,
                    163,
                    184,
                    0.14
                );

            box-shadow:
                0 4px 14px
                rgba(
                    70,
                    90,
                    130,
                    0.06
                );
        }


        .sidebar-user-label {

            font-size: 9px;

            font-weight: 700;

            letter-spacing: 0.7px;

            color: #94a3b8;

            margin-bottom: 3px;
        }


        .sidebar-user-name {

            font-size: 13px;

            font-weight: 700;

            color: #334155;

            word-break: break-word;
        }


        /* =========================================================
           GENERAL BUTTONS
           ========================================================= */

        .stButton > button {

            border-radius: 8px;

            border:
                1px solid
                rgba(
                    148,
                    163,
                    184,
                    0.25
                );

            font-weight: 600;

            transition:
                transform 0.15s ease,
                box-shadow 0.15s ease;
        }


        .stButton > button:hover {

            transform: translateY(-1px);

            box-shadow:
                0 5px 15px
                rgba(
                    59,
                    91,
                    150,
                    0.10
                );
        }


        /* =========================================================
           GENERAL INPUTS
           ========================================================= */

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {

            border-radius: 8px !important;
        }


        /* =========================================================
           RESPONSIVE
           ========================================================= */

        @media (max-width: 900px) {

            .auth-logo-wrapper {

                height: 125px;
            }

            .auth-logo {

                width: 125px;
                height: 125px;
            }

            .auth-title {

                font-size: 26px;
            }

            .st-key-auth-card {

                width: min(
                    560px,
                    calc(100vw - 32px)
                ) !important;

                max-width:
                    calc(100vw - 32px) !important;
            }

            .auth-tech-row,
            .auth-footer {

                width:
                    min(
                        560px,
                        calc(100vw - 32px)
                    );
            }

            .floating-card-doc {

                left: 70px;
            }

            .floating-card-chart {

                left: 60px;
            }

            .floating-card-job {

                right: 60px;
            }

            .floating-card-study {

                right: 60px;
            }
        }


        @media (max-width: 640px) {

            .auth-page-spacer {

                height: 10px;
            }

            .auth-logo-wrapper {

                height: 105px;
            }

            .auth-logo {

                width: 105px;
                height: 105px;
            }

            .auth-heading {

                margin-bottom: 14px;
            }

            .auth-title {

                font-size: 23px;
            }

            .auth-subtitle {

                font-size: 9px;
            }

            .st-key-auth-card {

                width:
                    calc(100vw - 24px) !important;

                max-width:
                    calc(100vw - 24px) !important;

                padding:
                    10px
                    12px
                    15px
                    12px !important;
            }

            .auth-tech-row {

                gap: 7px;

                font-size: 8px;
            }

            .auth-footer {

                width:
                    calc(100vw - 24px);
            }

            .floating-card {

                width: 38px;
                height: 38px;

                font-size: 14px;
            }

            .floating-card-doc {

                left: 18px;
                top: 180px;
            }

            .floating-card-job {

                right: 18px;
                top: 180px;
            }

            .floating-card-chart {

                left: 15px;
                top: 430px;
            }

            .floating-card-study {

                right: 15px;
                top: 430px;
            }

            .auth-grid {

                display: none;
            }

            .auth-dots {

                display: none;
            }
        }


        /* =========================================================
           HIDE AUTH BACKGROUND ON NON-AUTH PAGES
           ========================================================= */

        .auth-background {
            pointer-events: none;
        }


        </style>
        """
    )

# ------------------------------------------------------------
# Reusable HTML helpers
# ------------------------------------------------------------

def hero(title, subtitle, badges=None):
    badges = badges or []

    chips = "".join(
        f'<span class="badge">{b}</span>'
        for b in badges
    )

    st.markdown(
        f"""
        <div class="hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
            <div>{chips}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(icon, title, sub=""):
    sub_html = (
        f'<div class="sub">{sub}</div>'
        if sub
        else ""
    )

    st.markdown(
        f"""
        <div class="section-header">
            <span class="icon">{icon}</span>
            <span class="title">{title}</span>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def score_class(value):
    try:
        v = float(value)
    except (TypeError, ValueError):
        return ""

    if v >= 75:
        return "good"

    if v >= 50:
        return "warn"

    return "bad"


def score_card(
    label,
    value,
    sub="",
    suffix="%"
):
    cls = score_class(value)

    st.markdown(
        f"""
        <div class="card-score {cls}">
            <div class="label">{label}</div>

            <div class="value">
                {value}{suffix}
            </div>

            <div class="sub">
                {sub}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chip_row(items, kind):
    """
    kind = 'matched' | 'partial' | 'missing'
    """

    if not items:
        st.markdown(
            f"""
            <span class="chip {kind}">
                none
            </span>
            """,
            unsafe_allow_html=True,
        )
        return

    html = "".join(
        f'<span class="chip {kind}">{item}</span>'
        for item in items
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def sidebar_brand():
    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="logo">
                📄 Resume AI
            </div>

            <div class="tag">
                Analyzer · Matcher · Coach
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_section(title):
    st.markdown(
        f"""
        <div class="sidebar-section">
            {title}
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_item(text):
    st.markdown(
        f"""
        <div class="sidebar-item">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        """
        <div class="app-footer">
            AI Resume Analyzer ·
            Python ·
            Streamlit ·
            Groq ·
            MySQL ·
            FAISS
        </div>
        """,
        unsafe_allow_html=True,
    )


def loading_bar():
    """Show a moving blue bar at the top of the page."""

    placeholder = st.empty()

    placeholder.markdown(
        """
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background:
                linear-gradient(
                    90deg,
                    #2563eb,
                    #60a5fa,
                    #2563eb
                );
            background-size: 200% 100%;
            animation:
                slide 1.2s linear infinite;
            z-index: 999999;
        "></div>

        <style>

        @keyframes slide {

            0% {
                background-position: 0% 0;
            }

            100% {
                background-position: 200% 0;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    return placeholder