import importlib.util
import sys
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


MODULE_NAME = "event_attestation_module"


def load_module(relative_path: str, module_name: str):
    path = ROOT / relative_path
    parent_dir = str(path.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    # CRITICAL: Register module in sys.modules BEFORE exec_module so dataclass decorator can find it
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class EventAttestationTests(unittest.TestCase):
    def setUp(self):
        event_module = load_module("core-engine/event_attestation.py", MODULE_NAME)
        self.EventAttestation = event_module.EventAttestation
        self.EventType = event_module.EventType
        self.EventClaim = event_module.EventClaim
        self.WitnessSignature = event_module.WitnessSignature
        self.IoTCorroboration = event_module.IoTCorroboration
        self.attestation = self.EventAttestation()

    def test_create_event_claim(self):
        claim = self.attestation.create_event_claim(
            event_type=self.EventType.EMERGENCY_RESCUE,
            participant_id="firefighter_001",
            context={"location": "Building 7, Sector 4", "victims": 3},
        )
        self.assertIsInstance(claim, self.EventClaim)
        self.assertEqual(claim.event_type, self.EventType.EMERGENCY_RESCUE)
        self.assertEqual(claim.participant_id, "firefighter_001")
        self.assertEqual(claim.status, "OPEN")
        self.assertTrue(claim.claim_id.startswith("evt_"))

    def test_add_witness_signature_basic(self):
        claim = self.attestation.create_event_claim(
            event_type=self.EventType.MUTUAL_AID,
            participant_id="user_a",
            context={"action": "shared food"},
        )

        result = self.attestation.add_witness_signature(
            claim_id=claim.claim_id,
            witness_pubkey="witness_001",
            signature="sig_abc123",
        )
        self.assertEqual(result["status"], "WITNESS_THRESHOLD_MET")
        self.assertEqual(result["witnesses"], 1)
        self.assertEqual(result["threshold"], 1)

    def test_witness_threshold_not_met(self):
        claim = self.attestation.create_event_claim(
            event_type=self.EventType.EMERGENCY_RESCUE,
            participant_id="medic_001",
            context={"location": "Accident site"},
        )

        result = self.attestation.add_witness_signature(
            claim_id=claim.claim_id,
            witness_pubkey="witness_001",
            signature="sig_1",
        )
        self.assertEqual(result["status"], "WITNESS_ADDED")
        self.assertEqual(result["witnesses"], 1)
        self.assertEqual(result["threshold"], 3)

    def test_witness_threshold_met_after_multiple(self):
        claim = self.attestation.create_event_claim(
            event_type=self.EventType.MEDICAL_AID,
            participant_id="medic_002",
            context={"patient": "injured hiker"},
        )

        for i in range(3):
            result = self.attestation.add_witness_signature(
                claim_id=claim.claim_id,
                witness_pubkey=f"witness_{i}",
                signature=f"sig_{i}",
            )

        self.assertEqual(result["status"], "WITNESS_THRESHOLD_MET")
        self.assertEqual(result["witnesses"], 3)

    def test_add_iot_corroboration(self):
        claim = self.attestation.create_event_claim(
            event_type=self.EventType.EMERGENCY_RESCUE,
            participant_id="firefighter_002",
            context={"building": "Tower A"},
        )

        result = self.attestation.corroborate_with_iot(
            claim_id=claim.claim_id,
            sensor_id="temp_sensor_001",
            telemetry_hash="abc123def456",
            sensor_type="temperature",
            confidence=0.9,
        )
        self.assertEqual(result["status"], "IOT_ADDED")
        self.assertEqual(result["total_corroborations"], 1)

    def test_finalize_claim_insufficient_witnesses(self):
        claim = self.attestation.create_event_claim(
            event_type=self.EventType.EMERGENCY_RESCUE,
            participant_id="firefighter_003",
            context={},
        )

        result = self.attestation.finalize_claim(claim.claim_id)
        self.assertEqual(result["status"], "REJECTED")
        self.assertIn("Insufficient witnesses", result["reason"])

    def test_finalize_claim_success(self):
        claim = self.attestation.create_event_claim(
            event_type=self.EventType.MEDICAL_AID,
            participant_id="medic_003",
            context={"patient": "cardiac arrest"},
        )

        for i in range(3):
            self.attestation.add_witness_signature(
                claim_id=claim.claim_id,
                witness_pubkey=f"witness_{i}",
                signature=f"sig_{i}",
            )

        self.attestation.corroborate_with_iot(
            claim_id=claim.claim_id,
            sensor_id="vitals_monitor_001",
            telemetry_hash="vitals_hash_123",
            sensor_type="vitals",
            confidence=0.95,
        )

        result = self.attestation.finalize_claim(claim.claim_id)
        self.assertEqual(result["status"], "FINALIZED")
        self.assertIn("verification_score", result)
        self.assertIn("gini_penalty", result)
        self.assertIn("contribution", result)

        contrib = result["contribution"]
        self.assertIn("type", contrib)
        self.assertIn("verification_score", contrib)
        self.assertIn("timestamp", contrib)
        self.assertIn("gini_coefficient", contrib)
        self.assertEqual(contrib["type"], "life_saved")

    def test_gini_penalty_circular_witnesses(self):
        event_module = load_module("core-engine/event_attestation.py", f"{MODULE_NAME}_gini")
        EventAttestationGini = event_module.EventAttestation
        attestation = EventAttestationGini(enable_gini_collusion_check=True)

        claim = attestation.create_event_claim(
            event_type=event_module.EventType.MUTUAL_AID,
            participant_id="user_b",
            context={},
        )

        for i in range(3):
            attestation.add_witness_signature(
                claim_id=claim.claim_id,
                witness_pubkey="same_witness",
                signature=f"sig_{i}",
            )

        result = attestation.finalize_claim(claim.claim_id)
        self.assertEqual(result["status"], "FINALIZED")
        self.assertGreater(result["gini_penalty"], 0.0)
        self.assertLessEqual(result["gini_penalty"], 0.3)

    def test_no_gini_penalty_when_disabled(self):
        event_module = load_module("core-engine/event_attestation.py", f"{MODULE_NAME}_no_gini")
        EventAttestationNoGini = event_module.EventAttestation
        attestation = EventAttestationNoGini(enable_gini_collusion_check=False)

        claim = attestation.create_event_claim(
            event_type=event_module.EventType.MUTUAL_AID,
            participant_id="user_c",
            context={},
        )

        for i in range(3):
            attestation.add_witness_signature(
                claim_id=claim.claim_id,
                witness_pubkey="same_witness",
                signature=f"sig_{i}",
            )

        result = attestation.finalize_claim(claim.claim_id)
        self.assertEqual(result["gini_penalty"], 0.0)

    def test_get_claim_status(self):
        claim = self.attestation.create_event_claim(
            event_type=self.EventType.INFRASTRUCTURE_REPAIR,
            participant_id="engineer_001",
            context={"bridge": "River Crossing"},
        )

        self.attestation.add_witness_signature(
            claim_id=claim.claim_id,
            witness_pubkey="witness_001",
            signature="sig_1",
        )

        status = self.attestation.get_claim_status(claim.claim_id)
        self.assertIsNotNone(status)
        self.assertEqual(status["event_type"], "infrastructure_repair")
        self.assertEqual(status["witness_count"], 1)
        self.assertEqual(status["status"], "WITNESS_COLLECTING")

    def test_get_claim_status_not_found(self):
        status = self.attestation.get_claim_status("nonexistent_claim")
        self.assertIsNone(status)

    def test_event_type_categories_mapping(self):
        test_cases = [
            (self.EventType.EMERGENCY_RESCUE, "life_saved"),
            (self.EventType.MEDICAL_AID, "life_saved"),
            (self.EventType.INFRASTRUCTURE_REPAIR, "bridge_built"),
            (self.EventType.MUTUAL_AID, "community_organization"),
        ]

        for event_type, expected_category in test_cases:
            claim = self.attestation.create_event_claim(
                event_type=event_type,
                participant_id="test_user",
                context={},
            )
            threshold = self.attestation.min_witness_thresholds[event_type]
            for i in range(threshold):
                self.attestation.add_witness_signature(
                    claim_id=claim.claim_id,
                    witness_pubkey=f"w_{i}",
                    signature=f"s_{i}",
                )

            result = self.attestation.finalize_claim(claim.claim_id)
            self.assertEqual(result["status"], "FINALIZED")
            self.assertEqual(result["contribution"]["type"], expected_category)

    def test_process_contribution_into_reputation(self):
        event_module = load_module("core-engine/event_attestation.py", f"{MODULE_NAME}_rep")
        EventAttestationRep = event_module.EventAttestation
        attestation = EventAttestationRep()

        claim = attestation.create_event_claim(
            event_type=event_module.EventType.MEDICAL_AID,
            participant_id="medic_004",
            context={},
        )

        for i in range(3):
            attestation.add_witness_signature(
                claim_id=claim.claim_id,
                witness_pubkey=f"witness_{i}",
                signature=f"sig_{i}",
            )

        current_time = time.time()

        result = attestation.process_contribution_into_reputation(
            claim_id=claim.claim_id,
            current_time=current_time,
            existing_contributions=[],
            caste="MEDIC",
        )

        self.assertEqual(result["status"], "SUCCESS")
        self.assertIn("new_kinetic_reputation", result)
        self.assertIsInstance(result["new_kinetic_reputation"], float)
        self.assertGreater(result["new_kinetic_reputation"], 0)


if __name__ == "__main__":
    unittest.main()