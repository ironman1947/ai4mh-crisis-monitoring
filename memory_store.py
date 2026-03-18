"""
memory_store.py
AI4MH — Longitudinal SQLite memory store

Stores daily CSS scores per county for long-term trend analysis.
Enables the system to detect whether a region is getting
progressively worse over weeks or months — not just today.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


DB_PATH = "ai4mh_memory.db"


def initialize_db(db_path: str = DB_PATH):
    """
    Creates the database and tables if they don't exist.
    Called once on system startup.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS county_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            county TEXT NOT NULL,
            date TEXT NOT NULL,
            css_score REAL,
            confidence REAL,
            post_count INTEGER,
            si_score REAL,
            vs_score REAL,
            gc_score REAL,
            bot_flag INTEGER DEFAULT 0,
            media_flag INTEGER DEFAULT 0,
            sparse_flag INTEGER DEFAULT 0,
            escalation_level INTEGER DEFAULT 0,
            escalation_action TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            county TEXT NOT NULL,
            css_score REAL,
            confidence REAL,
            escalation_level INTEGER,
            flags TEXT,
            action_taken TEXT,
            reviewer_id TEXT,
            reviewer_decision TEXT,
            reviewer_timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


def store_daily_score(county_result: Dict, db_path: str = DB_PATH):
    """
    Stores a single county's CSS result for the day.

    Args:
        county_result: output dict from css_engine.run_css_pipeline()
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    escalation = county_result.get("escalation") or {}

    cursor.execute("""
        INSERT INTO county_scores (
            county, date, css_score, confidence, post_count,
            si_score, vs_score, gc_score,
            bot_flag, media_flag, sparse_flag,
            escalation_level, escalation_action
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        county_result.get("county"),
        datetime.now().strftime("%Y-%m-%d"),
        county_result.get("css"),
        county_result.get("confidence"),
        county_result.get("post_count"),
        county_result.get("si_score"),
        county_result.get("vs_score"),
        county_result.get("gc_score"),
        int(county_result.get("bot_flag", False)),
        int(county_result.get("media_flag", False)),
        int(county_result.get("status") == "SPARSE WARNING"),
        escalation.get("level", 0),
        escalation.get("action", "")
    ))

    conn.commit()
    conn.close()


def get_county_trend(
    county: str,
    days: int = 30,
    db_path: str = DB_PATH
) -> List[Dict]:
    """
    Retrieves CSS score history for a county over the last N days.
    Used for longitudinal trend analysis and prediction.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, css_score, confidence, escalation_level
        FROM county_scores
        WHERE county = ?
        ORDER BY date DESC
        LIMIT ?
    """, (county, days))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "date": row[0],
            "css_score": row[1],
            "confidence": row[2],
            "escalation_level": row[3]
        }
        for row in rows
    ]


def log_audit_event(
    county: str,
    css_score: float,
    confidence: float,
    escalation_level: int,
    flags: List[str],
    action_taken: str,
    reviewer_id: Optional[str] = None,
    reviewer_decision: Optional[str] = None,
    db_path: str = DB_PATH
):
    """
    Records every system action to the audit log.
    Every escalation, review, and human decision is logged here.
    Nothing is ever deleted from this table.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO audit_log (
            timestamp, county, css_score, confidence,
            escalation_level, flags, action_taken,
            reviewer_id, reviewer_decision, reviewer_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        county,
        css_score,
        confidence,
        escalation_level,
        ", ".join(flags) if flags else "none",
        action_taken,
        reviewer_id,
        reviewer_decision,
        datetime.now().isoformat() if reviewer_id else None
    ))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("Memory Store — Initialization Demo\n")
    initialize_db("demo_ai4mh.db")
    print("Database initialized: demo_ai4mh.db")
    print("Tables created: county_scores, audit_log")

    # Demo store
    mock_result = {
        "county": "Jefferson County",
        "status": "OK",
        "post_count": 320,
        "si_score": 0.78,
        "vs_score": 0.65,
        "gc_score": 1.0,
        "css": 0.862,
        "confidence": 0.74,
        "bot_flag": False,
        "media_flag": False,
        "escalation": {
            "level": 3,
            "action": "Alert State Behavioral Health Office"
        }
    }

    store_daily_score(mock_result, "demo_ai4mh.db")
    print("\nStored daily score for Jefferson County")

    log_audit_event(
        county="Jefferson County",
        css_score=0.862,
        confidence=0.74,
        escalation_level=3,
        flags=[],
        action_taken="Immediate escalation triggered",
        db_path="demo_ai4mh.db"
    )
    print("Audit event logged")

    trend = get_county_trend("Jefferson County", days=30, db_path="demo_ai4mh.db")
    print(f"\nTrend data retrieved: {len(trend)} records")
