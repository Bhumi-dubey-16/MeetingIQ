from typing import Optional, List
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Fix Render's postgres:// prefix — same fix as ATS scorer
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Fall back to SQLite locally if DATABASE_URL not set
if not DATABASE_URL:
    BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
    DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, '..', 'meetingiq.db')}"
    print(f"[DB] No DATABASE_URL found — using SQLite at {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

Base = declarative_base()


class Report(Base):
    __tablename__ = "reports"

    report_id  = Column(String(36),  primary_key=True)   # the uuid from run_agent
    transcript = Column(Text,        nullable=False)
    report_json = Column(Text,       nullable=False)      # full FullReport as JSON
    created_at = Column(DateTime,    default=datetime.utcnow)


# ── Init ───────────────────────────────────────────────────────────────────────

def init_db():
    Base.metadata.create_all(engine)


# ── Save ───────────────────────────────────────────────────────────────────────

def save_report(report_id: str, transcript: str, report_dict: dict):
    """
    Persists a report to the database.
    report_dict should be report.model_dump() — the full FullReport as a dict.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        record = Report(
            report_id   = report_id,
            transcript  = transcript,
            report_json = json.dumps(report_dict)
        )
        session.add(record)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ── Fetch one ─────────────────────────────────────────────────────────────────

def get_report(report_id: str) -> Optional[dict]:
    """
    Returns {"report_id", "report", "transcript", "created_at"} or None if not found.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        row = session.query(Report).filter(Report.report_id == report_id).first()
        if not row:
            return None
        return {
            "report_id"  : row.report_id,
            "report"     : json.loads(row.report_json),
            "transcript" : row.transcript,
            "created_at" : row.created_at.strftime("%Y-%m-%d %H:%M")
        }
    finally:
        session.close()


# ── Fetch recent ──────────────────────────────────────────────────────────────

def get_recent_reports(limit: int = 20) -> List[dict]:
    """
    Returns the most recent N reports — useful for a dashboard later.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        rows = (
            session.query(Report)
            .order_by(Report.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "report_id"  : row.report_id,
                "created_at" : row.created_at.strftime("%Y-%m-%d %H:%M"),
                "summary"    : json.loads(row.report_json).get("summary", {}).get("one_line", "")
            }
            for row in rows
        ]
    finally:
        session.close()