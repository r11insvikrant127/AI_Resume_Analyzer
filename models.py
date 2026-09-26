# models.py

from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime,
    ForeignKey, JSON, Boolean,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    resumes = relationship("Resume", back_populates="user")
    analyses = relationship("Analysis", back_populates="user")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)
    raw_text = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="resumes")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    resume_name = Column(String(255), nullable=False)

    jd_text = Column(Text, nullable=False)

    ats_score = Column(Float, nullable=False)
    required_match_percentage = Column(Float, nullable=False)
    technical_skill_percentage = Column(Float, nullable=False)
    good_to_have_match_percentage = Column(Float, nullable=False)

    result_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="analyses")


class RankingRun(Base):
    __tablename__ = "ranking_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    jd_text = Column(Text, nullable=False)
    rankings_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True, index=True)
    resume_name = Column(String(255), nullable=True)
    mode = Column(String(32), nullable=False)   # "simulation" | "qa"
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    messages = relationship("ChatMessage", back_populates="session",
                            cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"),
                        nullable=False, index=True)
    role = Column(String(16), nullable=False)   # "system"|"user"|"assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ChatSession", back_populates="messages")


class RagCompany(Base):
    __tablename__ = "rag_companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company = Column(String(255), unique=True, nullable=False, index=True)
    doc_count = Column(Integer, default=0, nullable=False)
    chunk_count = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False,
                        onupdate=datetime.utcnow)