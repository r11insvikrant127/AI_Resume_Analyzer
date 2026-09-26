# styles.py

import streamlit as st


THEME_CSS = """
<style>

/* ============================================================
   GLOBAL
   ============================================================ */

:root {
    --bg:         #f8fafc;
    --panel:      #ffffff;
    --border:     #e2e8f0;
    --text:       #0f172a;
    --muted:      #64748b;
    --accent:     #2563eb;
    --accent-2:   #1d4ed8;
    --success:    #16a34a;
    --warning:    #d97706;
    --danger:     #dc2626;
    --radius:     12px;
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1300px;
}

/* Tighten default Streamlit spacing a touch */
h1, h2, h3 { letter-spacing: -0.01em; }

/* ============================================================
   HERO HEADER
   ============================================================ */

.hero {
    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
    color: #ffffff;
    padding: 28px 32px;
    border-radius: var(--radius);
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -10px rgba(30, 58, 138, 0.5);
}

.hero h1 {
    margin: 0 0 6px 0;
    font-size: 32px;
    font-weight: 700;
    color: #ffffff;
}

.hero p {
    margin: 0;
    font-size: 15px;
    opacity: 0.9;
    color: #e0e7ff;
}

.hero .badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    color: #ffffff;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    margin-right: 6px;
    margin-top: 8px;
}

/* ============================================================
   SECTION HEADER
   ============================================================ */

.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--border);
}

.section-header .icon {
    font-size: 22px;
}

.section-header .title {
    font-size: 20px;
    font-weight: 600;
    color: var(--text);
}

.section-header .sub {
    font-size: 13px;
    color: var(--muted);
    margin-left: auto;
}

/* ============================================================
   CARDS
   ============================================================ */

.card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}

.card-score {
    background: var(--panel);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: var(--radius);
    padding: 16px 20px;
    text-align: left;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}

.card-score.good   { border-left-color: var(--success); }
.card-score.warn   { border-left-color: var(--warning); }
.card-score.bad    { border-left-color: var(--danger); }

.card-score .label {
    font-size: 12px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}

.card-score .value {
    font-size: 28px;
    font-weight: 700;
    color: var(--text);
    line-height: 1.1;
}

.card-score .sub {
    font-size: 12px;
    color: var(--muted);
    margin-top: 4px;
}

/* ============================================================
   FORMULA BLOCK
   ============================================================ */

.formula {
    font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    background: #f1f5f9;
    color: #0f172a;
    padding: 16px 20px;
    border-radius: var(--radius);
    border: 1px solid var(--border);
    font-size: 13px;
    line-height: 1.9;
}

.formula b { color: var(--accent-2); }

/* ============================================================
   REQUIREMENT CHIPS
   ============================================================ */

.chip {
    display: inline-block;
    padding: 4px 10px;
    margin: 3px 6px 3px 0;
    border-radius: 999px;
    font-size: 13px;
    border: 1px solid transparent;
}

.chip.matched {
    background: #dcfce7;
    color: #166534;
    border-color: #bbf7d0;
}

.chip.partial {
    background: #fef3c7;
    color: #92400e;
    border-color: #fde68a;
}

.chip.missing {
    background: #fee2e2;
    color: #991b1b;
    border-color: #fecaca;
}

/* ============================================================
   SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .sidebar-brand {
    padding: 4px 4px 16px 4px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 12px;
}

[data-testid="stSidebar"] .sidebar-brand .logo {
    font-size: 24px;
    font-weight: 700;
    color: var(--text);
}

[data-testid="stSidebar"] .sidebar-brand .tag {
    font-size: 12px;
    color: var(--muted);
}

[data-testid="stSidebar"] .sidebar-section {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin: 16px 0 6px 0;
    font-weight: 600;
}

[data-testid="stSidebar"] .sidebar-item {
    font-size: 13px;
    color: var(--text);
    padding: 3px 0;
}

/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.15s ease;
}

.stButton > button[kind="primary"] {
    background: var(--accent);
    border-color: var(--accent);
    color: #ffffff;
}

.stButton > button[kind="primary"]:hover {
    background: var(--accent-2);
    border-color: var(--accent-2);
}

/* ============================================================
   METRICS
   ============================================================ */

[data-testid="stMetricValue"] {
    font-weight: 700;
    color: var(--text);
}

[data-testid="stMetricLabel"] {
    color: var(--muted);
    font-size: 12px;
}

/* ============================================================
   EXPANDERS / TABS
   ============================================================ */

.streamlit-expanderHeader {
    font-weight: 600;
    color: var(--text);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 8px 16px;
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    background: #eff6ff;
    color: var(--accent-2);
}

/* ============================================================
   DATAFRAMES
   ============================================================ */

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
}

/* ============================================================
   FOOTER
   ============================================================ */

.app-footer {
    text-align: center;
    color: var(--muted);
    font-size: 12px;
    padding: 24px 0 8px 0;
    border-top: 1px solid var(--border);
    margin-top: 40px;
}

/* ============================================================
   HIDE STREAMLIT CHROME
   ============================================================ */

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
"""


def inject_theme():
    """Call once per page, right after st.set_page_config."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)


# ------------------------------------------------------------
# Reusable HTML helpers
# ------------------------------------------------------------

def hero(title, subtitle, badges=None):
    badges = badges or []
    chips = "".join(f'<span class="badge">{b}</span>' for b in badges)
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
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
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


def score_card(label, value, sub="", suffix="%"):
    cls = score_class(value)
    st.markdown(
        f"""
        <div class="card-score {cls}">
            <div class="label">{label}</div>
            <div class="value">{value}{suffix}</div>
            <div class="sub">{sub}</div>
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
            f'<span class="chip {kind}">none</span>',
            unsafe_allow_html=True,
        )
        return
    html = "".join(
        f'<span class="chip {kind}">{item}</span>' for item in items
    )
    st.markdown(html, unsafe_allow_html=True)


def sidebar_brand():
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="logo">📄 Resume AI</div>
            <div class="tag">Analyzer · Matcher · Coach</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_section(title):
    st.markdown(
        f'<div class="sidebar-section">{title}</div>',
        unsafe_allow_html=True,
    )


def sidebar_item(text):
    st.markdown(
        f'<div class="sidebar-item">{text}</div>',
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        """
        <div class="app-footer">
            AI Resume Analyzer · Python · Streamlit · Groq · MySQL · FAISS
        </div>
        """,
        unsafe_allow_html=True,
    )

def inject_theme():
    if st.session_state.get("_theme_injected"):
        return
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    st.session_state["_theme_injected"] = True