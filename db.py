import os
from pathlib import Path
from contextlib import contextmanager

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from models import Base


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)


# ============================================================
# DATABASE URL
# Streamlit Cloud → st.secrets
# Local development → .env
# ============================================================

try:
    DATABASE_URL = st.secrets["DATABASE_URL"]
except Exception:
    DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing. "
        "Add it to Streamlit Secrets or your .env file."
    )


# ============================================================
# CLEAN DATABASE URL
# ============================================================

db_url = make_url(DATABASE_URL)

# Remove URL-based ssl parameter.
# PyMySQL expects SSL configuration as a dictionary,
# not the string "true".
if "ssl" in db_url.query:
    query = dict(db_url.query)
    query.pop("ssl", None)
    db_url = db_url.set(query=query)


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    pool_recycle=280,
    connect_args={
        "ssl": {},
        "connect_timeout": 30,
    },
    future=True,
)


# ============================================================
# SESSION
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():
    """Create all tables if they do not yet exist."""
    Base.metadata.create_all(bind=engine)


# ============================================================
# DATABASE SESSION CONTEXT MANAGER
# ============================================================

@contextmanager
def get_session():
    """Yield a session and guarantee cleanup."""

    session = SessionLocal()

    try:
        yield session
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


# ============================================================
# STREAMLIT CACHED DATABASE INITIALIZATION
# ============================================================

@st.cache_resource(show_spinner=False)
def init_db_cached():
    """
    Run schema creation once per Streamlit process.
    """
    init_db()
    return True