# db_operations.py

from db import get_session
from models import User, Resume, Analysis, RankingRun


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