#!/usr/bin/env python3
"""
Business Memory - Persistent storage for Solomon Empire
Handles all memory, state, and data persistence
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path("memory")
MEMORY_DIR.mkdir(exist_ok=True)

DB_PATH = MEMORY_DIR / "solomon_empire.db"
MEMORY_BANK = MEMORY_DIR / "solomon_memory_bank.json"


def initialize_database():
    """Initialize SQLite database with all required tables."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            potential_revenue REAL DEFAULT 0,
            status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            contact TEXT,
            message TEXT,
            direction TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS revenue_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            source TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            content_type TEXT,
            content TEXT,
            status TEXT DEFAULT 'draft',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✓ Database initialized")


def add_business_opportunity(title, description="", potential_revenue=0.0):
    """Add a new business opportunity to memory."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO business_opportunities (title, description, potential_revenue) VALUES (?, ?, ?)",
        (title, description, potential_revenue)
    )
    conn.commit()
    opp_id = cursor.lastrowid
    conn.close()
    return {"id": opp_id, "title": title, "description": description, "potential_revenue": potential_revenue}


def add_conversation(platform, contact, message, direction="inbound"):
    """Log a conversation to memory."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (platform, contact, message, direction) VALUES (?, ?, ?, ?)",
        (platform, contact, message, direction)
    )
    conn.commit()
    conn_id = cursor.lastrowid
    conn.close()
    return {"id": conn_id, "platform": platform, "contact": contact}


def get_memory_snapshot():
    """Get a full snapshot of memory state."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM business_opportunities")
        opp_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM conversations")
        conv_count = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(amount) FROM revenue_events")
        total_revenue = cursor.fetchone()[0] or 0.0

        cursor.execute(
            "SELECT title, potential_revenue, status FROM business_opportunities ORDER BY created_at DESC LIMIT 5"
        )
        recent_opps = [{"title": r[0], "potential_revenue": r[1], "status": r[2]} for r in cursor.fetchall()]

        conn.close()

        return {
            "opportunities": opp_count,
            "conversations": conv_count,
            "total_revenue_logged": total_revenue,
            "recent_opportunities": recent_opps,
            "snapshot_time": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "snapshot_time": datetime.now().isoformat()}


def get_openclaw_payload():
    """Get payload formatted for OpenClaw API."""
    snapshot = get_memory_snapshot()
    return {
        "system": "solomon_empire",
        "timestamp": snapshot.get("snapshot_time"),
        "metrics": {
            "opportunities": snapshot.get("opportunities", 0),
            "conversations": snapshot.get("conversations", 0),
            "revenue": snapshot.get("total_revenue_logged", 0)
        }
    }


def save_to_memory_bank(key, value):
    """Save a key-value pair to the JSON memory bank."""
    data = {}
    if MEMORY_BANK.exists():
        with open(MEMORY_BANK) as f:
            data = json.load(f)

    data[key] = {"value": value, "updated_at": datetime.now().isoformat()}

    with open(MEMORY_BANK, "w") as f:
        json.dump(data, f, indent=2)


def get_from_memory_bank(key, default=None):
    """Retrieve a value from the JSON memory bank."""
    if not MEMORY_BANK.exists():
        return default
    with open(MEMORY_BANK) as f:
        data = json.load(f)
    return data.get(key, {}).get("value", default)


if __name__ == "__main__":
    initialize_database()
    print("Memory bank initialized at:", MEMORY_BANK)
    print("Snapshot:", json.dumps(get_memory_snapshot(), indent=2))
