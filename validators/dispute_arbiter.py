# =====================================================================
# NEXUS KORNET ENGINE: DISPUTE ARBITER v0.2
# Optimistic consensus with challenge window and slashing
# =====================================================================

from __future__ import annotations

import json
import sys
import time
from typing import Any, Dict, Optional, Set


def _log(level: str, message: str, **kwargs: Any) -> None:
    entry = {"timestamp": time.time(), "level": level, "message": message}
    entry.update(kwargs)
    print(json.dumps(entry, ensure_ascii=False), file=sys.stderr if level == "ERROR" else sys.stdout)


class DisputeError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.code = "DISPUTE_ERROR"


class DisputeArbiter:
    def __init__(self, challenge_window_days: int = 7) -> None:
        if challenge_window_days < 1:
            raise ValueError("challenge_window_days must be >= 1")
        self.challenge_window_seconds = challenge_window_days * 24 * 3600
        self.pending_disputes: Dict[str, Dict[str, Any]] = {}
        self.slashed_oracles: Set[str] = set()

    def open_dispute(
        self,
        action_id: str,
        challenger: str,
        evidence: str,
        oracle_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not action_id or not challenger or not evidence:
            raise DisputeError("action_id, challenger, and evidence are required")

        dispute = {
            "action_id": action_id,
            "challenger": challenger,
            "evidence": evidence,
            "oracle_id": oracle_id,
            "opened_at": time.time(),
            "status": "OPEN",
        }
        self.pending_disputes[action_id] = dispute
        _log("INFO", "dispute_opened", action_id=action_id, challenger=challenger, oracle_id=oracle_id)
        return dispute

    def resolve_dispute(self, action_id: str, jury_decision: str) -> Dict[str, Any]:
        dispute = self.pending_disputes.get(action_id)
        if not dispute:
            _log("WARNING", "dispute_not_found", action_id=action_id)
            return {"status": "NOT_FOUND"}

        if jury_decision not in ("CHEATING", "UPHELD"):
            raise DisputeError(f"Invalid jury_decision: {jury_decision}")

        dispute["status"] = "RESOLVED"
        dispute["decision"] = jury_decision

        if jury_decision == "CHEATING":
            oracle_id = dispute.get("oracle_id")
            if oracle_id is not None:
                self.slashed_oracles.add(oracle_id)
            _log("WARNING", "oracle_slashed", action_id=action_id, oracle_id=oracle_id)
            return {"status": "RESOLVED", "action": "SLASHED", "oracle_id": oracle_id}

        _log("INFO", "dispute_upheld", action_id=action_id)
        return {"status": "RESOLVED", "action": "UPHELD"}

    def is_in_challenge_window(self, action_timestamp: float) -> bool:
        return (time.time() - action_timestamp) < self.challenge_window_seconds
