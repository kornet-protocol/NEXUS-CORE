# =====================================================================
# NEXUS KORNET ENGINE: EVENT-DRIVEN HUMAN ATTESTATION v0.1
# Bridges human-to-human deeds (firefighters, medics, P2P mutual aid) into protocol
# Integrates with reputation_decay.py for verified contribution processing
# =====================================================================

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    from .reputation_decay import calculate_reputation
    from .logging import get_logger
except ImportError:
    from reputation_decay import calculate_reputation
    from logging import get_logger

logger = get_logger("event_attestation")


class EventType(Enum):
    EMERGENCY_RESCUE = "emergency_rescue"
    MEDICAL_AID = "medical_aid"
    INFRASTRUCTURE_REPAIR = "infrastructure_repair"
    MUTUAL_AID = "mutual_aid"


@dataclass
class WitnessSignature:
    witness_pubkey: str
    signature: str
    location_zk_proof: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class IoTCorroboration:
    sensor_id: str
    telemetry_hash: str
    sensor_type: str  # "temperature", "vitals", "gas", "motion"
    confidence: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class EventClaim:
    claim_id: str
    event_type: EventType
    participant_id: str
    context: Dict[str, Any]
    created_at: float
    witness_signatures: List[WitnessSignature] = field(default_factory=list)
    iot_corroborations: List[IoTCorroboration] = field(default_factory=list)
    status: str = "OPEN"  # OPEN, WITNESS_COLLECTING, IOT_CORROBORATING, FINALIZED, REJECTED
    verification_score: float = 0.0
    gini_penalty: float = 0.0


class EventAttestation:
    """
    Event-Driven Human Attestation for P2P good deeds.

    Supports: firefighters, medics, infrastructure repair, mutual aid.
    Requires dynamic witness thresholds and IoT corroboration for high-risk deeds.
    """

    # Minimum witness thresholds per event type
    WITNESS_THRESHOLDS = {
        EventType.EMERGENCY_RESCUE: 3,
        EventType.MEDICAL_AID: 3,
        EventType.INFRASTRUCTURE_REPAIR: 2,
        EventType.MUTUAL_AID: 1,
    }

    # Base verification scores per event type (before witness/IoT bonuses)
    BASE_VERIFICATION_SCORES = {
        EventType.EMERGENCY_RESCUE: 0.7,
        EventType.MEDICAL_AID: 0.7,
        EventType.INFRASTRUCTURE_REPAIR: 0.6,
        EventType.MUTUAL_AID: 0.5,
    }

    # IoT corroboration bonus per sensor type
    IOT_SENSOR_BONUSES = {
        "temperature": 0.05,      # Fire rescue: temperature sensors
        "vitals": 0.10,           # Medical aid: heart rate, SpO2
        "gas": 0.08,              # Hazardous environment: CO, CO2, CH4
        "motion": 0.03,           # Movement/presence detection
        "pressure": 0.05,         # Structural integrity
        "humidity": 0.02,         # Environmental conditions
    }

    def __init__(
        self,
        min_witness_threshold_override: Optional[Dict[EventType, int]] = None,
        enable_gini_collusion_check: bool = True,
        max_witness_distance_km: float = 5.0,
    ) -> None:
        self.claims: Dict[str, EventClaim] = {}
        self.min_witness_thresholds = self.WITNESS_THRESHOLDS.copy()
        if min_witness_threshold_override:
            self.min_witness_thresholds.update(min_witness_threshold_override)
        self.enable_gini_collusion_check = enable_gini_collusion_check
        self.max_witness_distance_km = max_witness_distance_km

    def create_event_claim(
        self,
        event_type: EventType,
        participant_id: str,
        context: Dict[str, Any],
        sensor_hashes: Optional[List[str]] = None,
    ) -> EventClaim:
        """
        Create a new event claim for human-to-human deed attestation.

        Args:
            event_type: Type of deed (EMERGENCY_RESCUE, MEDICAL_AID, etc.)
            participant_id: Soulbound identity of the claimant
            context: Free-form context (location description, description of deed, etc.)
            sensor_hashes: Optional list of IoT sensor data hashes pre-bound to event
        """
        claim_id = f"evt_{uuid.uuid4().hex[:16]}"

        claim = EventClaim(
            claim_id=claim_id,
            event_type=event_type,
            participant_id=participant_id,
            context=context,
            created_at=time.time(),
        )

        # Pre-bind IoT sensor hashes if provided
        if sensor_hashes:
            for sensor_hash in sensor_hashes:
                claim.iot_corroborations.append(IoTCorroboration(
                    sensor_id="prebound",
                    telemetry_hash=sensor_hash,
                    sensor_type="prebound",
                    confidence=0.5,
                ))

        self.claims[claim_id] = claim
        logger.info(
            "event_claim_created",
            claim_id=claim_id,
            event_type=event_type.value,
            participant=participant_id,
        )
        return claim

    def add_witness_signature(
        self,
        claim_id: str,
        witness_pubkey: str,
        signature: str,
        witness_location_zk: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add a witness signature to an event claim.

        Witness must be a verified human (via WebOfTrust) and provide ZK location proof
        for high-risk events (rescue, medical).
        """
        claim = self.claims.get(claim_id)
        if not claim:
            return {"status": "REJECTED", "reason": "Claim not found"}

        if claim.status not in ("OPEN", "WITNESS_COLLECTING"):
            return {
                "status": "REJECTED",
                "reason": f"Claim in {claim.status} state, cannot add witnesses",
            }

        claim.status = "WITNESS_COLLECTING"

        witness = WitnessSignature(
            witness_pubkey=witness_pubkey,
            signature=signature,
            location_zk_proof=witness_location_zk,
        )
        claim.witness_signatures.append(witness)

        logger.info(
            "witness_added",
            claim_id=claim_id,
            witness=witness_pubkey,
            total=len(claim.witness_signatures),
        )

        # Check if witness threshold met
        threshold = self.min_witness_thresholds.get(claim.event_type, 1)
        if len(claim.witness_signatures) >= threshold:
            return {
                "status": "WITNESS_THRESHOLD_MET",
                "witnesses": len(claim.witness_signatures),
                "threshold": threshold,
            }

        return {
            "status": "WITNESS_ADDED",
            "witnesses": len(claim.witness_signatures),
            "threshold": threshold,
        }

    def corroborate_with_iot(
        self,
        claim_id: str,
        sensor_id: str,
        telemetry_hash: str,
        sensor_type: str,
        confidence: float,
    ) -> Dict[str, Any]:
        """
        Corroborate event claim with IoT sensor telemetry.

        Binds environmental/equipment sensor readings to verify high-risk deeds.
        """
        claim = self.claims.get(claim_id)
        if not claim:
            return {"status": "REJECTED", "reason": "Claim not found"}

        if claim.status not in ("OPEN", "WITNESS_COLLECTING", "IOT_CORROBORATING"):
            return {
                "status": "REJECTED",
                "reason": f"Claim in {claim.status} state, cannot add IoT corroboration",
            }

        claim.status = "IOT_CORROBORATING"

        corroboration = IoTCorroboration(
            sensor_id=sensor_id,
            telemetry_hash=telemetry_hash,
            sensor_type=sensor_type,
            confidence=max(0.0, min(1.0, confidence)),
        )
        claim.iot_corroborations.append(corroboration)

        logger.info(
            "iot_corroboration_added",
            claim_id=claim_id,
            sensor_id=sensor_id,
            sensor_type=sensor_type,
        )

        return {"status": "IOT_ADDED", "total_corroborations": len(claim.iot_corroborations)}

    def _calculate_gini_penalty(self, claim: EventClaim) -> float:
        """
        Calculate Gini coefficient penalty for circular witness rings (collusion prevention).

        If witnesses all endorse each other in a tight cluster, penalty increases.
        """
        if not self.enable_gini_collusion_check:
            return 0.0

        if len(claim.witness_signatures) < 2:
            return 0.0

        # Simple proxy: check if witnesses are the same small set across recent claims
        # In production, this would query the WebOfTrust graph for clique detection
        witness_pubkeys = [w.witness_pubkey for w in claim.witness_signatures]
        unique_witnesses = len(set(witness_pubkeys))
        total_witnesses = len(witness_pubkeys)

        if total_witnesses == 0:
            return 0.0

        # Gini-like concentration: 1.0 = all same witness, 0.0 = all unique
        concentration = 1.0 - (unique_witnesses / total_witnesses)
        # Scale to max 0.3 penalty (30% reduction in verification score)
        return concentration * 0.3

    def _calculate_verification_score(self, claim: EventClaim) -> float:
        """
        Calculate final verification score V_k for the event claim.

        Components:
        - Base score for event type
        - Witness bonus (each witness above threshold adds confidence)
        - IoT corroboration bonus (sensor-type specific)
        - Gini penalty for collusion
        """
        base_score = self.BASE_VERIFICATION_SCORES.get(claim.event_type, 0.5)

        # Witness bonus
        threshold = self.min_witness_thresholds.get(claim.event_type, 1)
        witness_count = len(claim.witness_signatures)
        witness_bonus = 0.0
        if witness_count > threshold:
            # Each additional witness above threshold adds 0.02, max 0.15
            witness_bonus = min(0.15, (witness_count - threshold) * 0.02)
        elif witness_count == threshold:
            witness_bonus = 0.05  # Meeting threshold exactly

        # IoT corroboration bonus
        iot_bonus = 0.0
        for corr in claim.iot_corroborations:
            sensor_bonus = self.IOT_SENSOR_BONUSES.get(corr.sensor_type, 0.01)
            iot_bonus += sensor_bonus * corr.confidence
        iot_bonus = min(0.20, iot_bonus)  # Cap at 20%

        # Gini penalty
        gini_penalty = self._calculate_gini_penalty(claim)

        final_score = base_score + witness_bonus + iot_bonus - gini_penalty
        return max(0.0, min(1.0, final_score))

    def finalize_claim(self, claim_id: str) -> Dict[str, Any]:
        """
        Finalize the event claim and compute verification score V_k.

        Returns contribution data ready for reputation_decay.py processing.
        """
        claim = self.claims.get(claim_id)
        if not claim:
            return {"status": "REJECTED", "reason": "Claim not found"}

        if claim.status == "FINALIZED":
            return {
                "status": "ALREADY_FINALIZED",
                "verification_score": claim.verification_score,
            }

        # Check minimum witness threshold
        threshold = self.min_witness_thresholds.get(claim.event_type, 1)
        if len(claim.witness_signatures) < threshold:
            claim.status = "REJECTED"
            logger.warning(
                "claim_rejected_insufficient_witnesses",
                claim_id=claim_id,
                witnesses=len(claim.witness_signatures),
                threshold=threshold,
            )
            return {
                "status": "REJECTED",
                "reason": f"Insufficient witnesses: {len(claim.witness_signatures)}/{threshold}",
            }

        # Calculate verification score
        verification_score = self._calculate_verification_score(claim)
        gini_penalty = self._calculate_gini_penalty(claim)

        claim.verification_score = verification_score
        claim.gini_penalty = gini_penalty
        claim.status = "FINALIZED"

        # Prepare contribution for reputation engine
        # Map event type to reputation category
        category_map = {
            EventType.EMERGENCY_RESCUE: "life_saved",
            EventType.MEDICAL_AID: "life_saved",
            EventType.INFRASTRUCTURE_REPAIR: "bridge_built",
            EventType.MUTUAL_AID: "community_organization",
        }

        contribution = {
            "type": category_map.get(claim.event_type, "community_organization"),
            "verification_score": verification_score,
            "timestamp": claim.created_at,
            "gini_coefficient": gini_penalty,
            "event_claim_id": claim_id,
            "event_type": claim.event_type.value,
            "participant_id": claim.participant_id,
            "witness_count": len(claim.witness_signatures),
            "iot_corroboration_count": len(claim.iot_corroborations),
        }

        logger.info(
            "claim_finalized",
            claim_id=claim_id,
            verification_score=verification_score,
            gini_penalty=gini_penalty,
            category=contribution["type"],
        )

        return {
            "status": "FINALIZED",
            "claim_id": claim_id,
            "verification_score": verification_score,
            "gini_penalty": gini_penalty,
            "contribution": contribution,
        }

    def get_claim_status(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an event claim."""
        claim = self.claims.get(claim_id)
        if not claim:
            return None
        return {
            "claim_id": claim.claim_id,
            "event_type": claim.event_type.value,
            "participant_id": claim.participant_id,
            "status": claim.status,
            "witness_count": len(claim.witness_signatures),
            "iot_corroborations_count": len(claim.iot_corroborations),
            "verification_score": claim.verification_score,
            "gini_penalty": claim.gini_penalty,
            "created_at": claim.created_at,
        }

    def process_contribution_into_reputation(
        self,
        claim_id: str,
        current_time: float,
        existing_contributions: List[Dict[str, Any]],
        caste: str = "default",
        synthesis_multiplier: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Process finalized claim into reputation engine.

        Returns updated ReputationState with new kinetic and HWM values.
        """
        finalize_result = self.finalize_claim(claim_id)
        if finalize_result["status"] != "FINALIZED":
            return {
                "status": "ERROR",
                "reason": finalize_result.get("reason", "Finalization failed"),
            }

        contribution = finalize_result["contribution"]

        # Add to existing contributions and recalculate reputation
        all_contributions = existing_contributions + [contribution]

        new_kinetic = calculate_reputation(
            contributions=all_contributions,
            current_time=current_time,
            caste=caste,
            synthesis_multiplier=synthesis_multiplier,
        )

        return {
            "status": "SUCCESS",
            "claim_id": claim_id,
            "new_kinetic_reputation": new_kinetic,
            "contribution": contribution,
        }
