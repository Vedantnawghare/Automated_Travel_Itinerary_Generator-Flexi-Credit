import os
import sqlite3
import json
from typing import Dict, Any, Optional, List


DEFAULT_DB_PATH = os.getenv("DATABASE_PATH", os.path.join("data", "travel_memory.db"))


def get_db_path(custom_path: Optional[str] = None) -> str:
    """Resolve the SQLite database path and ensure parent directory exists."""
    path = custom_path or os.getenv("DATABASE_PATH", DEFAULT_DB_PATH)
    parent_dir = os.path.dirname(path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
    return path


def initialize_db(db_path: Optional[str] = None) -> None:
    """Initialize SQLite tables for storing reusable travel preferences and past search memory."""
    path = get_db_path(db_path)
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Table 1: User Profile Preferences (stores aggregated preferences)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_key TEXT UNIQUE DEFAULT 'default_user',
            travel_style TEXT,
            interests TEXT, -- JSON array of interests
            avoid TEXT,     -- JSON array of dislikes/avoidances
            accommodation_preference TEXT,
            transportation_preference TEXT,
            notes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table 2: Travel Trip History (stores past planned trips for recall)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trip_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT,
            origin TEXT,
            duration INTEGER,
            travellers INTEGER,
            budget REAL,
            travel_style TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_preferences(
    travel_style: Optional[str] = None,
    interests: Optional[List[str]] = None,
    avoid: Optional[List[str]] = None,
    accommodation_preference: Optional[str] = None,
    transportation_preference: Optional[str] = None,
    notes: Optional[str] = None,
    user_key: str = "default_user",
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Save or update travel preferences in SQLite."""
    path = get_db_path(db_path)
    initialize_db(path)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Get existing preferences first to merge
    cursor.execute("SELECT travel_style, interests, avoid, accommodation_preference, transportation_preference, notes FROM user_preferences WHERE user_key = ?", (user_key,))
    row = cursor.fetchone()

    existing_interests = []
    existing_avoid = []
    if row:
        try:
            existing_interests = json.loads(row[1]) if row[1] else []
        except Exception:
            existing_interests = []
        try:
            existing_avoid = json.loads(row[2]) if row[2] else []
        except Exception:
            existing_avoid = []

    merged_interests = list(set((existing_interests or []) + (interests or [])))
    merged_avoid = list(set((existing_avoid or []) + (avoid or [])))
    final_style = travel_style or (row[0] if row else "balanced")
    final_accom = accommodation_preference or (row[3] if row else "mid-range hotel")
    final_trans = transportation_preference or (row[4] if row else "flight / train / cab")
    final_notes = notes or (row[5] if row else "")

    cursor.execute("""
        INSERT INTO user_preferences (user_key, travel_style, interests, avoid, accommodation_preference, transportation_preference, notes, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_key) DO UPDATE SET
            travel_style=excluded.travel_style,
            interests=excluded.interests,
            avoid=excluded.avoid,
            accommodation_preference=excluded.accommodation_preference,
            transportation_preference=excluded.transportation_preference,
            notes=excluded.notes,
            updated_at=CURRENT_TIMESTAMP
    """, (
        user_key,
        final_style,
        json.dumps(merged_interests),
        json.dumps(merged_avoid),
        final_accom,
        final_trans,
        final_notes
    ))

    conn.commit()
    conn.close()

    return {
        "user_key": user_key,
        "travel_style": final_style,
        "interests": merged_interests,
        "avoid": merged_avoid,
        "accommodation_preference": final_accom,
        "transportation_preference": final_trans,
        "notes": final_notes
    }


def get_preferences(user_key: str = "default_user", db_path: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve saved preferences from SQLite."""
    path = get_db_path(db_path)
    initialize_db(path)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT travel_style, interests, avoid, accommodation_preference, transportation_preference, notes
        FROM user_preferences WHERE user_key = ?
    """, (user_key,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "travel_style": "balanced",
            "interests": [],
            "avoid": [],
            "accommodation_preference": "mid-range hotel",
            "transportation_preference": "flight / train / cab",
            "notes": ""
        }

    try:
        interests = json.loads(row[1]) if row[1] else []
    except Exception:
        interests = []

    try:
        avoid = json.loads(row[2]) if row[2] else []
    except Exception:
        avoid = []

    return {
        "travel_style": row[0] or "balanced",
        "interests": interests,
        "avoid": avoid,
        "accommodation_preference": row[3] or "mid-range hotel",
        "transportation_preference": row[4] or "flight / train / cab",
        "notes": row[5] or ""
    }


def update_preferences(
    user_key: str = "default_user",
    updates: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function to update specific preference keys."""
    updates = updates or {}
    return save_preferences(
        travel_style=updates.get("travel_style"),
        interests=updates.get("interests"),
        avoid=updates.get("avoid"),
        accommodation_preference=updates.get("accommodation_preference"),
        transportation_preference=updates.get("transportation_preference"),
        notes=updates.get("notes"),
        user_key=user_key,
        db_path=db_path
    )


def record_trip_history(
    destination: str,
    origin: str,
    duration: int,
    travellers: int,
    budget: float,
    travel_style: str,
    db_path: Optional[str] = None
) -> None:
    """Save summary of a generated trip into past trip memory."""
    path = get_db_path(db_path)
    initialize_db(path)
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trip_history (destination, origin, duration, travellers, budget, travel_style)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (destination, origin, duration, travellers, budget, travel_style))
    conn.commit()
    conn.close()


def get_past_destinations(limit: int = 5, db_path: Optional[str] = None) -> List[str]:
    """Return recent destinations planned by the user."""
    path = get_db_path(db_path)
    initialize_db(path)
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT destination FROM trip_history ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]
