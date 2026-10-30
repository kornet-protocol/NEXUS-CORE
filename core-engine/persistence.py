# =====================================================================
# NEXUS KORNET ENGINE: PERSISTENCE LAYER v0.2
# SQLite-backed state for production fail-closed operation
# =====================================================================

from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


DB_PATH = Path("nexus_state.db")


@dataclass
class ContributionRecord:
    contribution_id: str
    user_id: str
    category: str
    impact: float
    verification_score: float
    timestamp: float
    gini_coefficient: float
    hardware_signature: Optional[str] = None
    zk_proof_hash: Optional[str] = None


class PersistenceLayer:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self._db_path = db_path
        self._local = threading.local()
        self._initialize_db()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False,
                isolation_level="DEFERRED",
            )
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return self._local.conn

    def _initialize_db(self) -> None:
        conn = self._get_conn()
        conn.executescript(
            """
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=NORMAL;
            PRAGMA busy_timeout=5000;

            CREATE TABLE IF NOT EXISTS contributions (
                contribution_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                category TEXT NOT NULL,
                impact REAL NOT NULL,
                verification_score REAL NOT NULL,
                timestamp REAL NOT NULL,
                gini_coefficient REAL NOT NULL DEFAULT 0.0,
                hardware_signature TEXT,
                zk_proof_hash TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS disputes (
                action_id TEXT PRIMARY KEY,
                challenger TEXT NOT NULL,
                evidence TEXT NOT NULL,
                oracle_id TEXT,
                opened_at REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'OPEN',
                decision TEXT,
                resolved_at REAL
            );

            CREATE TABLE IF NOT EXISTS telemetry_baselines (
                sensor_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                value REAL NOT NULL,
                raw_payload BLOB,
                PRIMARY KEY (sensor_id, timestamp)
            );

            CREATE TABLE IF NOT EXISTS skill_skills (
                user_id TEXT NOT NULL,
                skill TEXT NOT NULL,
                acquired_at REAL NOT NULL,
                PRIMARY KEY (user_id, skill)
            );

            CREATE INDEX IF NOT EXISTS idx_contributions_user
                ON contributions(user_id);
            CREATE INDEX IF NOT EXISTS idx_contributions_category
                ON contributions(category);
            CREATE INDEX IF NOT EXISTS idx_disputes_status
                ON disputes(status);
            """
        )
        conn.commit()

    def insert_contribution(self, record: ContributionRecord) -> None:
        conn = self._get_conn()
        conn.execute(
            """
            INSERT OR REPLACE INTO contributions
                (contribution_id, user_id, category, impact, verification_score,
                 timestamp, gini_coefficient, hardware_signature, zk_proof_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.contribution_id,
                record.user_id,
                record.category,
                record.impact,
                record.verification_score,
                record.timestamp,
                record.gini_coefficient,
                record.hardware_signature,
                record.zk_proof_hash,
            ),
        )
        conn.commit()

    def get_contributions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        if user_id is not None:
            rows = conn.execute(
                "SELECT * FROM contributions WHERE user_id = ? ORDER BY timestamp DESC",
                (user_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM contributions ORDER BY timestamp DESC").fetchall()
        return [dict(row) for row in rows]

    def insert_dispute(
        self,
        action_id: str,
        challenger: str,
        evidence: str,
        oracle_id: Optional[str] = None,
        opened_at: Optional[float] = None,
    ) -> None:
        conn = self._get_conn()
        conn.execute(
            """
            INSERT OR REPLACE INTO disputes
                (action_id, challenger, evidence, oracle_id, opened_at, status)
            VALUES (?, ?, ?, ?, ?, 'OPEN')
            """,
            (action_id, challenger, evidence, oracle_id, opened_at),
        )
        conn.commit()

    def update_dispute(self, action_id: str, decision: str, resolved_at: float) -> None:
        conn = self._get_conn()
        conn.execute(
            """
            UPDATE disputes SET status = 'RESOLVED', decision = ?, resolved_at = ?
            WHERE action_id = ?
            """,
            (decision, resolved_at, action_id),
        )
        conn.commit()

    def get_open_disputes(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM disputes WHERE status = 'OPEN' ORDER BY opened_at ASC"
        ).fetchall()
        return [dict(row) for row in rows]

    def insert_telemetry_baseline(
        self, sensor_id: str, timestamp: float, value: float, raw_payload: Optional[bytes] = None
    ) -> None:
        conn = self._get_conn()
        conn.execute(
            """
            INSERT OR REPLACE INTO telemetry_baselines (sensor_id, timestamp, value, raw_payload)
            VALUES (?, ?, ?, ?)
            """,
            (sensor_id, timestamp, value, raw_payload),
        )
        conn.commit()

    def get_telemetry_baseline(self, sensor_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            """
            SELECT sensor_id, timestamp, value FROM telemetry_baselines
            WHERE sensor_id = ? ORDER BY timestamp DESC LIMIT ?
            """,
            (sensor_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]

    def insert_skill(self, user_id: str, skill: str, acquired_at: float) -> None:
        conn = self._get_conn()
        conn.execute(
            """
            INSERT OR IGNORE INTO skill_skills (user_id, skill, acquired_at)
            VALUES (?, ?, ?)
            """,
            (user_id, skill, acquired_at),
        )
        conn.commit()

    def get_user_skills(self, user_id: str) -> List[str]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT skill FROM skill_skills WHERE user_id = ?", (user_id,)
        ).fetchall()
        return [row["skill"] for row in rows]

    def close(self) -> None:
        if hasattr(self._local, "conn") and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None
