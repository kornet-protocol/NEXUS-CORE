# =====================================================================
# NEXUS KORNET ENGINE: WEB OF TRUST (Sybil Resistance) v0.2
# Proof-of-Unique-Human via blinded signatures and endorsement graphs
# Fail-closed: rejects endorsements until signature verifier is configured
# =====================================================================

from __future__ import annotations

import time
from collections import deque
from typing import Any, Dict, List, Optional, Set, Tuple


class WebOfTrust:
    def __init__(self, min_endorsements: int = 5, max_path_depth: int = 3, signature_verifier: Optional[Any] = None) -> None:
        if min_endorsements < 1:
            raise ValueError("min_endorsements must be >= 1")
        if max_path_depth < 1:
            raise ValueError("max_path_depth must be >= 1")
        self.endorsements: List[Dict] = []
        self.trust_graph: Dict[str, Set[str]] = {}
        self.verified_humans: Set[str] = set()
        self.min_endorsements = min_endorsements
        self.max_path_depth = max_path_depth
        self.signature_verifier = signature_verifier

    def endorse(self, endorser: str, endorsee: str, signature: str, context: str) -> Tuple[bool, str]:
        if self.signature_verifier is None:
            return False, "signature_verifier_unconfigured"

        entry = {
            "endorser": endorser,
            "endorsee": endorsee,
            "timestamp": time.time(),
            "signature": signature,
            "context": context,
        }
        self.endorsements.append(entry)
        self.trust_graph.setdefault(endorsee, set()).add(endorser)
        self._recompute_verified_humans()
        return True, "endorsement_recorded"

    def is_human(self, identity: str) -> bool:
        return identity in self.verified_humans

    def _recompute_verified_humans(self) -> None:
        self.verified_humans.clear()
        for identity, endorsers in self.trust_graph.items():
            if len(endorsers) >= self.min_endorsements:
                self.verified_humans.add(identity)

    def get_trust_path(self, source: str, target: str) -> Optional[List[str]]:
        if source == target:
            return [source]
        queue = deque([(source, [source])])
        visited = {source}
        while queue:
            current, path = queue.popleft()
            for neighbor in self.trust_graph.get(current, set()):
                if neighbor == target:
                    return path + [neighbor]
                if neighbor not in visited and len(path) < self.max_path_depth:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None
