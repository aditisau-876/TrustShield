import sqlite3
from pathlib import Path


DB_PATH = Path("data/processed/threat_database.db")


def initialize_database():

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            domain TEXT,
            source TEXT,
            threat_type TEXT,
            confidence REAL DEFAULT 1.0,
            first_seen TEXT,
            last_seen TEXT
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_domain
        ON threats(domain)
    """)

    conn.commit()
    conn.close()


def add_threat(
    url,
    domain,
    source,
    threat_type="malicious",
    confidence=1.0,
    first_seen=None,
    last_seen=None
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO threats
        (
            url,
            domain,
            source,
            threat_type,
            confidence,
            first_seen,
            last_seen
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        url,
        domain,
        source,
        threat_type,
        confidence,
        first_seen,
        last_seen
    ))

    conn.commit()
    conn.close()


def lookup_url(url):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            url,
            domain,
            source,
            threat_type,
            confidence,
            first_seen,
            last_seen
        FROM threats
        WHERE url = ?
    """, (url,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return None

    return {
        "url": result[0],
        "domain": result[1],
        "source": result[2],
        "threat_type": result[3],
        "confidence": result[4],
        "first_seen": result[5],
        "last_seen": result[6]
    }


def lookup_domain(domain):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            url,
            domain,
            source,
            threat_type,
            confidence,
            first_seen,
            last_seen
        FROM threats
        WHERE domain = ?
        LIMIT 20
    """, (domain,))

    rows = cursor.fetchall()

    conn.close()

    results = []

    for row in rows:

        results.append({
            "url": row[0],
            "domain": row[1],
            "source": row[2],
            "threat_type": row[3],
            "confidence": row[4],
            "first_seen": row[5],
            "last_seen": row[6]
        })

    return results