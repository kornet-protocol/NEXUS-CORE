import sys
import math
import time
import unittest
from pathlib import Path

# Add core-engine to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core-engine"))

from graceful_degradation import (
    SyntheticStateProvider,
    KalmanFilter,
    ViableSystemModel,
    TelemetryReading,
    MaintenanceOrder,
)


class TestSyntheticStateProvider(unittest.TestCase):
    def setUp(self):
        self.provider = SyntheticStateProvider(history_hours=48)  # 2 days for tests

    def test_update_and_fallback_same_hour(self):
        """Update baseline and retrieve fallback for same hour."""
        timestamp = time.time()
        self.provider.update_baseline("temperature", timestamp, 25.0, 1.0)
        self.provider.update_baseline("temperature", timestamp + 10, 26.0, 1.0)

        fallback = self.provider.get_fallback_reading("temperature", timestamp)
        self.assertAlmostEqual(fallback, 25.5, places=1)

    def test_fallback_uses_weighted_average(self):
        """Trusted measurements with higher weight influence baseline more."""
        timestamp = time.time()
        # Low weight measurement (should not affect baseline since weight <= 0.7)
        self.provider.update_baseline("temperature", timestamp, 100.0, 0.5)
        # High weight measurement
        self.provider.update_baseline("temperature", timestamp + 10, 20.0, 1.0)

        fallback = self.provider.get_fallback_reading("temperature", timestamp)
        self.assertAlmostEqual(fallback, 20.0, places=1)

    def test_fallback_adjacent_hour(self):
        """If no data for current hour, uses adjacent hour."""
        timestamp = time.time()
        hour = int(time.localtime(timestamp).tm_hour)
        # Force a different hour for testing
        target_ts = timestamp - 3600 * 2  # 2 hours ago
        target_hour = int(time.localtime(target_ts).tm_hour)

        self.provider.update_baseline("humidity", target_ts, 60.0, 1.0)

        # Query for current hour (no data) -> should get adjacent hour
        fallback = self.provider.get_fallback_reading("humidity", timestamp)
        self.assertAlmostEqual(fallback, 60.0, places=1)

    def test_no_baseline_returns_zero(self):
        """Unknown metric type returns 0."""
        fallback = self.provider.get_fallback_reading("unknown_metric", time.time())
        self.assertEqual(fallback, 0.0)

    def test_has_baseline(self):
        """has_baseline returns True only after trusted updates."""
        self.assertFalse(self.provider.has_baseline("temperature"))
        self.provider.update_baseline("temperature", time.time(), 25.0, 1.0)
        self.assertTrue(self.provider.has_baseline("temperature"))


class TestKalmanFilter(unittest.TestCase):
    def test_initialization(self):
        """First measurement initializes state."""
        kf = KalmanFilter()
        result = kf.update(10.0)
        self.assertEqual(result, 10.0)

    def test_convergence(self):
        """Filter converges to true value over time (with steady-state lag)."""
        kf = KalmanFilter(process_variance=1e-4, measurement_variance=1e-2)
        for i in range(100):
            kf.update(5.0 + (i * 0.01))  # Slowly drifting
        # With q=1e-4, r=1e-2, steady-state lag ≈ q/r * drift_rate
        # Drift rate = 0.01/step, expected lag ~ 0.1
        self.assertAlmostEqual(kf.x, 5.9, places=1)

    def test_innovation_calculation(self):
        """Innovation returns measurement - prediction."""
        kf = KalmanFilter()
        kf.update(10.0)  # Initialize
        innov, innov_cov = kf.get_innovation(12.0)
        self.assertAlmostEqual(innov, 2.0, places=5)
        self.assertGreater(innov_cov, 0.0)


class TestViableSystemModelSoftWeights(unittest.TestCase):
    def setUp(self):
        self.provider = SyntheticStateProvider(history_hours=48)
        self.vsm = ViableSystemModel("test_node_1")
        self.vsm.register_sensor(
            "temp_1",
            "temperature",
            synthetic_provider=self.provider,
        )
        self.vsm.register_sensor(
            "temp_2",
            "temperature",
            synthetic_provider=self.provider,
        )

    def _create_reading(self, sensor_id: str, value: float) -> TelemetryReading:
        return TelemetryReading(
            sensor_id=sensor_id,
            timestamp=time.time(),
            value=value,
            raw_payload=b"test",
        )

    def test_normal_fluctuation_retains_weight_one(self):
        """Normal fluctuations (within 2 sigma) keep weight ≈ 1.0."""
        # Initialize with stable readings
        for i in range(20):
            reading = self._create_reading("temp_1", 25.0)
            is_trusted, status, _, weight = self.vsm.ingest_telemetry(reading)
            self.assertTrue(is_trusted)
            self.assertEqual(status, "ACCEPTED")

        # Normal small variation (well within 2 sigma: 0.1 jump when steady-state sigma ≈ 0.1)
        reading = self._create_reading("temp_1", 25.1)
        is_trusted, status, _, weight = self.vsm.ingest_telemetry(reading)
        self.assertTrue(is_trusted)
        self.assertEqual(status, "ACCEPTED")
        self.assertAlmostEqual(weight, 1.0, places=2)

    def test_sharp_spike_drops_weight(self):
        """Sudden sharp spike (lighter on sensor) drops weight toward 0."""
        # Initialize stable baseline
        for i in range(20):
            reading = self._create_reading("temp_1", 25.0)
            self.vsm.ingest_telemetry(reading)

        # Sharp spike: +40°C in one step (like lighter)
        reading = self._create_reading("temp_1", 65.0)
        is_trusted, status, _, weight = self.vsm.ingest_telemetry(reading)

        self.assertFalse(is_trusted)
        self.assertIn(status, ["DEGRADED", "SABOTAGE"])
        self.assertLess(weight, 0.1)  # Should be near 0 for 5+ sigma

    def test_exponential_degradation_zone(self):
        """Anomaly scores 2-5 sigma show exponential weight degradation."""
        # Initialize
        for i in range(20):
            self.vsm.ingest_telemetry(self._create_reading("temp_1", 25.0))

        # Craft a reading that gives ~3 sigma anomaly
        # We need to know the Kalman state. After 20 readings of 25.0, x ≈ 25.0, P ≈ R
        # Innovation of ~3*sqrt(R) where R=0.01 -> 3*0.1 = 0.3
        # Actually, let's just test the weight formula directly
        weights = []
        for score in [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
            w = self.vsm.calculate_weight(score)
            weights.append(w)

        self.assertEqual(weights[0], 1.0)  # 2 sigma = 1.0
        self.assertGreater(weights[1], weights[2])  # Monotonically decreasing
        self.assertGreater(weights[-2], weights[-1])
        # At exactly 5.0: exp(-0.8 * 3) ≈ 0.091
        # Zero weight only for score > 5.0
        self.assertAlmostEqual(weights[-1], 0.091, places=2)
        self.assertEqual(self.vsm.calculate_weight(5.1), 0.0)

    def test_system_never_shuts_down_on_sabotage(self):
        """System continues operating (no exception) even with sabotage."""
        # Initialize
        for i in range(20):
            self.vsm.ingest_telemetry(self._create_reading("temp_1", 25.0))

        # Sabotage sensor 1
        reading = self._create_reading("temp_1", 200.0)  # Extreme value
        try:
            is_trusted, status, filtered_val, weight = self.vsm.ingest_telemetry(reading)
            # Should not throw, should return gracefully
            self.assertFalse(is_trusted)
            self.assertEqual(status, "SABOTAGE")
            self.assertEqual(weight, 0.0)
            # Filtered value should still be reasonable (Kalman rejects innovation)
            self.assertLess(abs(filtered_val - 25.0), 10.0)
        except Exception as e:
            self.fail(f"System threw exception on sabotage: {e}")

    def test_synthetic_fallback_activated(self):
        """When sensor weight drops, synthetic fallback contributes."""
        # Build baseline first
        base_time = time.time()
        for h in range(24):
            ts = base_time + h * 3600
            self.provider.update_baseline("temperature", ts, 20.0 + h * 0.5, 1.0)

        # Initialize sensors
        for i in range(20):
            self.vsm.ingest_telemetry(self._create_reading("temp_1", 25.0))
            self.vsm.ingest_telemetry(self._create_reading("temp_2", 25.0))

        # Sabotage both sensors
        self.vsm.ingest_telemetry(self._create_reading("temp_1", 200.0))
        self.vsm.ingest_telemetry(self._create_reading("temp_2", 200.0))

        # Get effective state - should use synthetic
        eff_val, eff_weight, maint_order = self.vsm.get_effective_state("temperature")
        self.assertLess(eff_weight, 0.3)
        self.assertIsNotNone(maint_order)
        self.assertTrue(maint_order.synthetic_fallback)
        # Value should be near synthetic (around 20-30 range)
        self.assertGreater(eff_val, 15.0)
        self.assertLess(eff_val, 35.0)

    def test_maintenance_order_emitted(self):
        """MaintenanceOrder created when weight drops below threshold."""
        for i in range(20):
            self.vsm.ingest_telemetry(self._create_reading("temp_1", 25.0))

        # Spike triggers maintenance
        self.vsm.ingest_telemetry(self._create_reading("temp_1", 200.0))

        orders = self.vsm.get_pending_maintenance()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["sensor_id"], "temp_1")
        self.assertTrue(orders[0]["synthetic_fallback"])
        self.assertEqual(orders[0]["status"], "SABOTAGE")

    def test_clear_maintenance_after_calibration(self):
        """Maintenance orders cleared after physical calibration."""
        for i in range(20):
            self.vsm.ingest_telemetry(self._create_reading("temp_1", 25.0))
        self.vsm.ingest_telemetry(self._create_reading("temp_1", 200.0))

        self.assertEqual(len(self.vsm.get_pending_maintenance()), 1)
        cleared = self.vsm.clear_maintenance("temp_1")
        self.assertEqual(cleared, 1)
        self.assertEqual(len(self.vsm.get_pending_maintenance()), 0)

    def test_cluster_degraded_maintenance(self):
        """Cluster-level maintenance order when all sensors of a type degrade."""
        # Two temp sensors
        for i in range(20):
            self.vsm.ingest_telemetry(self._create_reading("temp_1", 25.0))
            self.vsm.ingest_telemetry(self._create_reading("temp_2", 25.0))

        # Sabotage both
        self.vsm.ingest_telemetry(self._create_reading("temp_1", 200.0))
        self.vsm.ingest_telemetry(self._create_reading("temp_2", 200.0))

        # Check cluster maintenance
        eff_val, eff_weight, maint = self.vsm.get_effective_state("temperature")
        self.assertIsNotNone(maint)
        self.assertEqual(maint.sensor_id, "cluster:temperature")
        self.assertEqual(maint.status, "CLUSTER_DEGRADED")


class TestExportState(unittest.TestCase):
    def test_vsm_export_contains_sensor_weights(self):
        vsm = ViableSystemModel("node_x")
        provider = SyntheticStateProvider()
        vsm.register_sensor("ph_1", "ph", synthetic_provider=provider)

        for i in range(5):
            vsm.ingest_telemetry(TelemetryReading(
                sensor_id="ph_1", timestamp=time.time(), value=7.0, raw_payload=b""
            ))

        state = vsm.export_vsm_state()
        self.assertIn("sensors", state)
        self.assertIn("ph_1", state["sensors"])
        self.assertIn("last_weight", state["sensors"]["ph_1"])
        self.assertIn("last_anomaly_score", state["sensors"]["ph_1"])

    def test_synthetic_provider_export(self):
        provider = SyntheticStateProvider()
        provider.update_baseline("temperature", time.time(), 25.0, 1.0)
        exported = provider.export_state()
        self.assertIn("temperature", exported)


if __name__ == "__main__":
    unittest.main()