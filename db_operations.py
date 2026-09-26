# db_operations.py

from db import get_session
from models import User, Resume, Analysis, RankingRun
from datetime import datetime
from models import User, Resume, Analysis, RankingRun, ChatSession, ChatMessage, RagCompany

def create_user(email, password_hash, full_name=None, is_admin=False):
    with get_session() as s:
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            full_name=full_name,
            is_admin=is_admin,
        )
        s.add(user)
        s.flush()
        return user.id


def get_user_by_email(email):
    with get_session() as s:
        return (
            s.query(User)
            .filter(User.email == email.lower().strip())
            .first()
        )


def get_user_by_id(user_id):
    with get_session() as s:
        return s.query(User).filter(User.id == user_id).first()


def list_all_users():
    with get_session() as s:
        return s.query(User).order_by(User.created_at.desc()).all()


def save_resume(user_id, filename, file_hash, raw_text):
    with get_session() as s:
        r = Resume(
            user_id=user_id,
            filename=filename,
            file_hash=file_hash,
            raw_text=raw_text,
        )
        s.add(r)
        s.flush()
        return r.id


def save_analysis(user_id, resume_id, resume_name, jd_text, result):
    with get_session() as s:
        a = Analysis(
            user_id=user_id,
            resume_id=resume_id,
            resume_name=resume_name,
            jd_text=jd_text,
            ats_score=result.get("ats_score", 0),
            required_match_percentage=result.get("required_match_percentage", 0),
            technical_skill_percentage=result.get("technical_skill_percentage", 0),
            good_to_have_match_percentage=result.get("good_to_have_match_percentage", 0),
            result_json=result,
        )
        s.add(a)
        s.flush()
        return a.id


def save_ranking_run(user_id, jd_text, rankings):
    with get_session() as s:
        rr = RankingRun(
            user_id=user_id,
            jd_text=jd_text,
            rankings_json=rankings,
        )
        s.add(rr)
        s.flush()
        return rr.id


def list_user_analyses(user_id, limit=50):
    with get_session() as s:
        return (
            s.query(Analysis)
            .filter(Analysis.user_id == user_id)
            .order_by(Analysis.created_at.desc())
            .limit(limit)
            .all()
        )


def list_all_analyses(limit=200):
    with get_session() as s:
        return (
            s.query(Analysis)
            .order_by(Analysis.created_at.desc())
            .limit(limit)
            .all()
        )

# ------------------------------------------------------------------
# HISTORY
# ------------------------------------------------------------------

def get_analysis_by_id(analysis_id, user_id=None):
    """Fetch a single analysis, optionally enforcing ownership."""
    with get_session() as s:
        q = s.query(Analysis).filter(Analysis.id == analysis_id)
        if user_id is not None:
            q = q.filter(Analysis.user_id == user_id)
        return q.first()


def delete_analysis(analysis_id, user_id):
    with get_session() as s:
        row = (
            s.query(Analysis)
            .filter(Analysis.id == analysis_id,
                    Analysis.user_id == user_id)
            .first()
        )
        if row:
            s.delete(row)
            return True
        return False


def list_user_analyses_with_pagination(user_id, offset=0, limit=20):
    with get_session() as s:
        return (
            s.query(Analysis)
            .filter(Analysis.user_id == user_id)
            .order_by(Analysis.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )


def count_user_analyses(user_id):
    with get_session() as s:
        return (
            s.query(Analysis)
            .filter(Analysis.user_id == user_id)
            .count()
        )


# ------------------------------------------------------------------
# CHAT
# ------------------------------------------------------------------

def create_chat_session(user_id, mode, analysis_id=None,
                        resume_name=None, title=None):
    with get_session() as s:
        cs = ChatSession(
            user_id=user_id,
            analysis_id=analysis_id,
            resume_name=resume_name,
            mode=mode,
            title=title or f"{mode} — {resume_name or 'new'}",
        )
        s.add(cs)
        s.flush()
        return cs.id


def append_chat_message(session_id, role, content):
    with get_session() as s:
        msg = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
        )
        s.add(msg)
        s.flush()
        return msg.id


def list_chat_messages(session_id):
    with get_session() as s:
        return (
            s.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )


def list_user_chat_sessions(user_id, limit=50):
    with get_session() as s:
        return (
            s.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
            .limit(limit)
            .all()
        )


def delete_chat_session(session_id, user_id):
    with get_session() as s:
        row = (
            s.query(ChatSession)
            .filter(ChatSession.id == session_id,
                    ChatSession.user_id == user_id)
            .first()
        )
        if row:
            s.delete(row)
            return True
        return False


# ------------------------------------------------------------------
# RAG
# ------------------------------------------------------------------

def upsert_rag_company(company, doc_count, chunk_count):
    with get_session() as s:
        row = (
            s.query(RagCompany)
            .filter(RagCompany.company == company)
            .first()
        )
        if row:
            row.doc_count = doc_count
            row.chunk_count = chunk_count
            row.updated_at = datetime.utcnow()
        else:
            s.add(RagCompany(
                company=company,
                doc_count=doc_count,
                chunk_count=chunk_count,
            ))


def list_rag_companies():
    with get_session() as s:
        return s.query(RagCompany).order_by(RagCompany.company.asc()).all()


def get_rag_company(company):
    with get_session() as s:
        return (
            s.query(RagCompany)
            .filter(RagCompany.company == company)
            .first()
        )