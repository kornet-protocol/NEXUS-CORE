# =====================================================================
# NEXUS KORNET ENGINE: PROOF-OF-ASSEMBLY MODULE v0.1
# Guerilla Manufacturing: micro-factory guild logic
# =====================================================================

from __future__ import annotations

import hashlib
import time
from typing import Any, Callable, Dict, List, Optional


class AssemblyGuild:
    def __init__(
        self,
        reward_per_device: float = 50.0,
        attestation_verifier: Optional[Callable[[str, str, str], bool]] = None,
    ) -> None:
        self.reward_per_device = reward_per_device
        self.assembled_devices: Dict[str, Dict[str, Any]] = {}
        self.active_devices: set = set()
        self.known_bom_hashes: set = set()
        self.attestation_verifier = attestation_verifier

    def register_bom(self, bom_hash: str) -> None:
        """Register reference BOM hash (Bill of Materials)."""
        self.known_bom_hashes.add(bom_hash)

    def compute_bom_hash(self, components: List[str]) -> str:
        """Deterministic hash of board component list."""
        canonical = sorted(components)
        payload = "|".join(canonical).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def attest_chip(
        self,
        device_id: str,
        public_key_attestation: str,
        signature: str = "",
    ) -> bool:
        """
        The verifier must validate the device challenge-response externally.
        """
        if not device_id or not public_key_attestation or self.attestation_verifier is None:
            return False
        return self.attestation_verifier(device_id, public_key_attestation, signature)

    def verify_bom_hash(self, device_id: str, bom_hash: str) -> bool:
        return bom_hash in self.known_bom_hashes

    def verify_assembly(
        self,
        device_id: str,
        signature: str,
        public_key_attestation: str,
        bom_hash: str,
    ) -> str:
        if not self.attest_chip(device_id, public_key_attestation, signature):
            return "REJECTED: Fake silicon"
        if not self.verify_bom_hash(device_id, bom_hash):
            return "REJECTED: Wrong components"
        self.activate_device(device_id, signature)
        return "ACCEPTED: Device online. Assembler rewarded."

    def activate_device(self, device_id: str, signature: str) -> None:
        self.assembled_devices[device_id] = {
            "activated_at": time.time(),
            "signature": signature,
            "status": "ONLINE",
        }
        self.active_devices.add(device_id)

    def reward_assembler(self, assembler_id: str) -> Dict[str, Any]:
        """Karma + stable reward for assembled and activated device."""
        return {
            "assembler": assembler_id,
            "karma": self.reward_per_device,
            "stable": self.reward_per_device * 0.1,
            "timestamp": time.time(),
        }

    def guild_stats(self) -> Dict[str, int]:
        return {
            "total_assembled": len(self.assembled_devices),
            "active": len(self.active_devices),
            "bom_specs": len(self.known_bom_hashes),
        }
