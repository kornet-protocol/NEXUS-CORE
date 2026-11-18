import sys
import unittest
from pathlib import Path

# Add core-engine to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core-engine"))

from status_stasis import StatusStasisManager, PeerStake


class TestStatusStasis(unittest.TestCase):
    def setUp(self):
        self.manager = StatusStasisManager(min_domains=3, max_gini_threshold=0.65)

    def test_single_domain_monopoly_rejected(self):
        # 3 peers, but all from 'Physics' domain -> must be rejected
        stakes = [
            PeerStake("peer_1", "Physics", 50.0, 1000.0),
            PeerStake("peer_2", "Physics", 50.0, 1200.0),
            PeerStake("peer_3", "Physics", 50.0, 1500.0),
        ]
        success, reason, _ = self.manager.apply_stasis(
            project_id="proj_mono",
            lead_id="lead_1",
            lead_current_r=500.0,
            lead_hwm=800.0,
            duration_sec=3600.0 * 24 * 30,
            stakes=stakes,
        )
        self.assertFalse(success)
        self.assertIn("Cross-domain diversity failed", reason)

    def test_valid_cross_domain_stasis_accepted(self):
        # Balanced stakes across Bio, Energy, Hardware -> accepted
        stakes = [
            PeerStake("peer_1", "Biology", 100.0, 1000.0),
            PeerStake("peer_2", "Energy", 100.0, 1200.0),
            PeerStake("peer_3", "Hardware", 100.0, 1500.0),
        ]
        success, reason, lambda_stasis = self.manager.apply_stasis(
            project_id="proj_valid",
            lead_id="lead_1",
            lead_current_r=500.0,
            lead_hwm=800.0,
            duration_sec=3600.0 * 24 * 60,
            stakes=stakes,
        )
        self.assertTrue(success)
        self.assertEqual(reason, "STASIS_GRANTED")
        self.assertLess(lambda_stasis, 0.2)  # Decay successfully dampened

    def test_fraud_slashing_cuts_hwm(self):
        stakes = [
            PeerStake("peer_1", "Biology", 100.0, 1000.0),
            PeerStake("peer_2", "Energy", 100.0, 1000.0),
            PeerStake("peer_3", "Hardware", 100.0, 1000.0),
        ]
        self.manager.apply_stasis(
            "proj_fraud", "lead_x", 300.0, 500.0, 3600.0 * 24, stakes
        )

        result = self.manager.settle_project("proj_fraud", is_fraud_or_abandoned=True)
        self.assertEqual(result["status"], "SLASHED")
        self.assertLess(result["new_lead_hwm"], 500.0)
        self.assertEqual(result["peer_hwm_haircuts"]["peer_1"], 900.0)  # 10% HWM cut

    def test_gini_calculation_perfect_diversity(self):
        # Equal stakes across 4 domains -> Gini = 0
        stakes = [
            PeerStake("p1", "A", 100.0, 1000.0),
            PeerStake("p2", "B", 100.0, 1000.0),
            PeerStake("p3", "C", 100.0, 1000.0),
            PeerStake("p4", "D", 100.0, 1000.0),
        ]
        gini = StatusStasisManager.calculate_domain_gini(stakes)
        self.assertAlmostEqual(gini, 0.0, places=5)

    def test_gini_calculation_monopoly(self):
        # One domain dominates -> Gini approaches (n-1)/n for n domains
        # With 3 domains, max Gini = 2/3 ≈ 0.667
        stakes = [
            PeerStake("p1", "A", 10000.0, 1000.0),
            PeerStake("p2", "B", 1.0, 1000.0),
            PeerStake("p3", "C", 1.0, 1000.0),
        ]
        gini = StatusStasisManager.calculate_domain_gini(stakes)
        self.assertGreater(gini, 0.6)
        self.assertLess(gini, 0.67)

    def test_gini_calculation_monopoly_many_domains(self):
        # With many domains, Gini can approach 1.0
        stakes = [
            PeerStake("p1", "A", 10000.0, 1000.0),
        ] + [PeerStake(f"p{i}", f"B{i}", 1.0, 1000.0) for i in range(2, 20)]
        gini = StatusStasisManager.calculate_domain_gini(stakes)
        self.assertGreater(gini, 0.8)

    def test_empty_stakes_rejected(self):
        success, reason, _ = self.manager.apply_stasis(
            project_id="proj_empty",
            lead_id="lead_1",
            lead_current_r=500.0,
            lead_hwm=800.0,
            duration_sec=3600.0,
            stakes=[],
        )
        self.assertFalse(success)

    def test_insufficient_domains_rejected(self):
        stakes = [
            PeerStake("peer_1", "Biology", 100.0, 1000.0),
            PeerStake("peer_2", "Energy", 100.0, 1000.0),
        ]  # Only 2 domains, need 3
        success, reason, _ = self.manager.apply_stasis(
            project_id="proj_2domains",
            lead_id="lead_1",
            lead_current_r=500.0,
            lead_hwm=800.0,
            duration_sec=3600.0,
            stakes=stakes,
        )
        self.assertFalse(success)
        self.assertIn("Cross-domain diversity failed", reason)

    def test_duration_cap_enforced(self):
        stakes = [
            PeerStake("peer_1", "Biology", 100.0, 1000.0),
            PeerStake("peer_2", "Energy", 100.0, 1000.0),
            PeerStake("peer_3", "Hardware", 100.0, 1000.0),
        ]
        # Duration > 24 months (63_072_000 sec)
        success, reason, _ = self.manager.apply_stasis(
            project_id="proj_long",
            lead_id="lead_1",
            lead_current_r=500.0,
            lead_hwm=800.0,
            duration_sec=63_072_001.0,
            stakes=stakes,
        )
        self.assertFalse(success)
        self.assertIn("Duration exceeds", reason)

    def test_success_distribution_returns_stakes_plus_royalty(self):
        stakes = [
            PeerStake("peer_1", "Biology", 100.0, 1000.0),
            PeerStake("peer_2", "Energy", 200.0, 1000.0),
            PeerStake("peer_3", "Hardware", 300.0, 1000.0),
        ]
        self.manager.apply_stasis(
            "proj_success", "lead_x", 300.0, 500.0, 3600.0 * 24, stakes
        )

        result = self.manager.settle_project("proj_success", is_fraud_or_abandoned=False, milestone_completion_ratio=1.0)
        self.assertEqual(result["status"], "REWARDED")
        # Total staked = 600, royalty pool = 60
        # peer_1: 100 + 60*(100/600) = 110
        # peer_2: 200 + 60*(200/600) = 220
        # peer_3: 300 + 60*(300/600) = 330
        self.assertAlmostEqual(result["peer_returns"]["peer_1"], 110.0)
        self.assertAlmostEqual(result["peer_returns"]["peer_2"], 220.0)
        self.assertAlmostEqual(result["peer_returns"]["peer_3"], 330.0)

    def test_partial_completion_no_slashing(self):
        stakes = [
            PeerStake("peer_1", "Biology", 100.0, 1000.0),
            PeerStake("peer_2", "Energy", 100.0, 1000.0),
            PeerStake("peer_3", "Hardware", 100.0, 1000.0),
        ]
        self.manager.apply_stasis(
            "proj_partial", "lead_x", 300.0, 500.0, 3600.0 * 24, stakes
        )

        # 50% completion - should be rewarded, not slashed
        result = self.manager.settle_project("proj_partial", is_fraud_or_abandoned=False, milestone_completion_ratio=0.5)
        self.assertEqual(result["status"], "REWARDED")

    def test_abandoned_project_slashed(self):
        stakes = [
            PeerStake("peer_1", "Biology", 100.0, 1000.0),
            PeerStake("peer_2", "Energy", 100.0, 1000.0),
            PeerStake("peer_3", "Hardware", 100.0, 1000.0),
        ]
        self.manager.apply_stasis(
            "proj_abandoned", "lead_x", 300.0, 500.0, 3600.0 * 24, stakes
        )

        # < 20% completion -> treated as abandoned/fraud
        result = self.manager.settle_project("proj_abandoned", is_fraud_or_abandoned=False, milestone_completion_ratio=0.1)
        self.assertEqual(result["status"], "SLASHED")

    def test_get_project_status(self):
        stakes = [
            PeerStake("peer_1", "Biology", 100.0, 1000.0),
            PeerStake("peer_2", "Energy", 100.0, 1000.0),
            PeerStake("peer_3", "Hardware", 100.0, 1000.0),
        ]
        self.manager.apply_stasis(
            "proj_status", "lead_x", 300.0, 500.0, 3600.0 * 24, stakes
        )

        status = self.manager.get_project_status("proj_status")
        self.assertIsNotNone(status)
        self.assertEqual(status["project_id"], "proj_status")
        self.assertEqual(status["lead_id"], "lead_x")
        self.assertTrue(status["is_active"])
        self.assertFalse(status["is_settled"])
        self.assertEqual(status["num_peers"], 3)
        self.assertCountEqual(status["domains"], ["Biology", "Energy", "Hardware"])

    def test_invalid_inputs(self):
        # Negative lead_hwm
        stakes = [PeerStake("p1", "A", 100.0, 1000.0), PeerStake("p2", "B", 100.0, 1000.0), PeerStake("p3", "C", 100.0, 1000.0)]
        success, reason, _ = self.manager.apply_stasis(
            "proj_neg", "lead", 100.0, -100.0, 3600.0, stakes
        )
        self.assertFalse(success)

        # Zero duration
        success, reason, _ = self.manager.apply_stasis(
            "proj_zero", "lead", 100.0, 100.0, 0.0, stakes
        )
        self.assertFalse(success)

        # Missing project_id
        success, reason, _ = self.manager.apply_stasis(
            "", "lead", 100.0, 100.0, 3600.0, stakes
        )
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()