# =====================================================================
# NEXUS KORNET ENGINE: GRACEFUL DEGRADATION MODULE v0.4
# Stafford Beer's Viable System Model + Soft Kalman Weights + Synthetic State Provider
# Anti-DoS Resilience: Never fully shuts down — degrades to synthetic extrapolation
# =====================================================================

import math
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple, Any

try:
    from .logging import get_logger
except ImportError:
    from logging import get_logger

logger = get_logger("nexus.graceful_degradation")


@dataclass
class TelemetryReading:
    sensor_id: str
    timestamp: float
    value: float
    raw_payload: bytes
    hardware_signature: Optional[str] = None


@dataclass
class MaintenanceOrder:
    node_id: str
    sensor_id: str
    status: str
    synthetic_fallback: bool
    anomaly_score: float
    weight: float
    timestamp: float
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "sensor_id": self.sensor_id,
            "status": self.status,
            "synthetic_fallback": self.synthetic_fallback,
            "anomaly_score": self.anomaly_score,
            "weight": self.weight,
            "timestamp": self.timestamp,
            "details": self.details,
        }


class SyntheticStateProvider:
    """
    Maintains historical baseline profiles per metric type, keyed by hour of day.
    Provides deterministic cyclic fallback when sensor data is untrusted.
    Only updates baselines with trusted measurements (weight > 0.7).
    """

    def __init__(self, history_hours: int = 336):  # 14 days * 24 hours = 336 hours
        self.history_hours = history_hours
        # metric_type -> hour_of_day -> list of (timestamp, value, weight)
        self.baselines: Dict[str, Dict[int, List[Tuple[float, float, float]]]] = {}
        # metric_type -> hour_of_day -> running mean
        self.hourly_means: Dict[str, Dict[int, float]] = {}

    def _get_hour_key(self, timestamp: float) -> int:
        """Extract hour of day (0-23) from timestamp."""
        return int(time.localtime(timestamp).tm_hour)

    def update_baseline(
        self, metric_type: str, timestamp: float, trusted_value: float, weight: float
    ) -> None:
        """
        Updates the rolling moving average baseline using only measurements
        with weight > 0.7 (trusted zone).
        """
        if weight <= 0.7:
            return  # Discard untrusted measurements from baseline

        hour = self._get_hour_key(timestamp)

        if metric_type not in self.baselines:
            self.baselines[metric_type] = {}
            self.hourly_means[metric_type] = {}

        if hour not in self.baselines[metric_type]:
            self.baselines[metric_type][hour] = []

        self.baselines[metric_type][hour].append((timestamp, trusted_value, weight))

        # Keep only last N hours of data per hour bucket
        cutoff = timestamp - (self.history_hours * 3600)
        self.baselines[metric_type][hour] = [
            (ts, val, w) for ts, val, w in self.baselines[metric_type][hour] if ts > cutoff
        ]

        # Recompute running mean for this hour
        if self.baselines[metric_type][hour]:
            total_weight = sum(w for _, _, w in self.baselines[metric_type][hour])
            if total_weight > 0:
                weighted_sum = sum(val * w for _, val, w in self.baselines[metric_type][hour])
                self.hourly_means[metric_type][hour] = weighted_sum / total_weight

    def get_fallback_reading(self, metric_type: str, timestamp: float) -> float:
        """
        Returns the deterministic cyclic historical mean for that hour
        if sensor data is untrusted or missing.
        """
        hour = self._get_hour_key(timestamp)

        if metric_type in self.hourly_means and hour in self.hourly_means[metric_type]:
            return self.hourly_means[metric_type][hour]

        # If no history for this hour, try adjacent hours (circular)
        for offset in range(1, 24):
            for direction in [-1, 1]:
                adj_hour = (hour + direction * offset) % 24
                if metric_type in self.hourly_means and adj_hour in self.hourly_means[metric_type]:
                    return self.hourly_means[metric_type][adj_hour]

        # Ultimate fallback: return 0 (caller should handle)
        return 0.0

    def has_baseline(self, metric_type: str) -> bool:
        """Check if we have any baseline data for this metric type."""
        return metric_type in self.hourly_means and len(self.hourly_means[metric_type]) > 0

    def export_state(self) -> Dict:
        return {
            metric: {str(h): len(vals) for h, vals in hours.items()}
            for metric, hours in self.baselines.items()
        }


class KalmanFilter:
    """
    Kalman Filter with innovation-based anomaly scoring.
    Tracks state (x) and covariance (P) for 1D measurements.
    """

    def __init__(
        self,
        process_variance: float = 1e-4,
        measurement_variance: float = 1e-2,
    ):
        self.x = 0.0  # State estimate
        self.p = 1.0  # Error covariance
        self.q = process_variance
        self.r = measurement_variance
        self.initialized = False

    def update(self, measurement: float) -> float:
        """Standard Kalman update. Returns filtered state estimate."""
        if not self.initialized:
            self.x = measurement
            self.initialized = True
            return self.x

        # Predict
        self.p += self.q

        # Update
        innovation = measurement - self.x
        innovation_cov = self.p + self.r
        k = self.p / innovation_cov
        self.x += k * innovation
        self.p = (1 - k) * self.p

        return self.x

    def get_innovation(self, measurement: float) -> Tuple[float, float]:
        """
        Returns (innovation, innovation_variance) for anomaly scoring.
        innovation = z - x_pred
        innovation_variance = P + R
        """
        if not self.initialized:
            return 0.0, self.r

        innovation = measurement - self.x
        innovation_cov = self.p + self.r
        return innovation, innovation_cov


@dataclass
class SensorProfile:
    sensor_id: str
    metric_type: str
    kalman: KalmanFilter = field(default_factory=KalmanFilter)
    synthetic_provider: Optional[SyntheticStateProvider] = None
    window_size: int = 100
    values: Deque[float] = field(default_factory=deque)
    timestamps: Deque[float] = field(default_factory=deque)
    weights: Deque[float] = field(default_factory=deque)
    last_update: float = 0.0
    last_weight: float = 1.0
    last_anomaly_score: float = 0.0

    def update_baselines(self, value: float, timestamp: float, weight: float) -> None:
        if self.synthetic_provider:
            self.synthetic_provider.update_baseline(
                self.metric_type, timestamp, value, weight
            )

        self.values.append(value)
        self.timestamps.append(timestamp)
        self.weights.append(weight)
        if len(self.values) > self.window_size:
            self.values.popleft()
            self.timestamps.popleft()
            self.weights.popleft()
        self.last_update = timestamp


class ViableSystemModel:
    """
    VSM with Soft Degradation:
    - Each sensor has a continuous trust weight w ∈ [0, 1]
    - System computes weighted average state
    - Falls back to synthetic provider when total weight drops
    - Emits MaintenanceOrder for physical calibration — NEVER shuts down
    """

    SOFT_WEIGHT_THRESHOLD = 0.3  # Below this -> synthetic fallback dominates
    GAMMA = 0.8  # Exponential decay rate for anomaly scores 2-5 sigma

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.sensors: Dict[str, SensorProfile] = {}
        self.is_island_mode: bool = False
        self.local_consensus_round: int = 0
        self.maintenance_orders: List[MaintenanceOrder] = []

    def register_sensor(
        self,
        sensor_id: str,
        metric_type: str,
        process_variance: float = 1e-4,
        measurement_variance: float = 1e-2,
        synthetic_provider: Optional[SyntheticStateProvider] = None,
    ) -> None:
        kalman = KalmanFilter(process_variance, measurement_variance)
        self.sensors[sensor_id] = SensorProfile(
            sensor_id=sensor_id,
            metric_type=metric_type,
            kalman=kalman,
            synthetic_provider=synthetic_provider,
        )

    def calculate_weight(self, anomaly_score: float) -> float:
        """
        Exponential dynamic weight based on normalized anomaly score.
        - score <= 2.0: w = 1.0 (normal noise)
        - 2.0 < score <= 5.0: w = exp(-γ * (score - 2.0)) (degradation)
        - score > 5.0: w = 0.0 (complete failure/sabotage)
        """
        if anomaly_score <= 2.0:
            return 1.0
        elif anomaly_score <= 5.0:
            return math.exp(-self.GAMMA * (anomaly_score - 2.0))
        else:
            return 0.0

    def ingest_telemetry(self, reading: TelemetryReading) -> Tuple[bool, str, float, float]:
        """
        Processes a telemetry reading.
        Returns: (is_trusted, status_message, filtered_value, weight)
        """
        profile = self.sensors.get(reading.sensor_id)
        if not profile:
            # Unknown sensor - accept with low weight
            logger.warning("unknown_sensor", sensor_id=reading.sensor_id)
            return True, "UNKNOWN_SENSOR_ACCEPTED", reading.value, 0.5

        kalman = profile.kalman
        innovation, innovation_cov = kalman.get_innovation(reading.value)

        # Normalized anomaly score
        if innovation_cov > 0:
            anomaly_score = abs(innovation) / math.sqrt(innovation_cov)
        else:
            anomaly_score = 0.0

        # Calculate dynamic weight
        weight = self.calculate_weight(anomaly_score)

        # Update Kalman: if weight is very low (sabotage), use extrapolated/predicted value
        # to prevent state corruption, otherwise use actual measurement
        if weight < 0.01:  # Effectively zero weight = sabotage
            # Use predicted state (extrapolation) for Kalman update
            predicted = kalman.x
            filtered_value = kalman.update(predicted)
        else:
            filtered_value = kalman.update(reading.value)

        # Update baselines only if trusted
        profile.update_baselines(reading.value, reading.timestamp, weight)
        profile.last_weight = weight
        profile.last_anomaly_score = anomaly_score

        # Determine status
        if weight >= 0.9:
            status = "ACCEPTED"
            is_trusted = True
        elif weight > 0.0:
            status = "DEGRADED"
            is_trusted = False
        else:
            status = "SABOTAGE"
            is_trusted = False

        # Check if system weight is critically low -> emit maintenance order
        if weight < self.SOFT_WEIGHT_THRESHOLD:
            order = MaintenanceOrder(
                node_id=self.node_id,
                sensor_id=reading.sensor_id,
                status=status,
                synthetic_fallback=True,
                anomaly_score=anomaly_score,
                weight=weight,
                timestamp=reading.timestamp,
                details=f"Sensor {reading.sensor_id} weight {weight:.3f} below threshold {self.SOFT_WEIGHT_THRESHOLD}. Synthetic fallback active.",
            )
            self.maintenance_orders.append(order)
            logger.warning("maintenance_order_created", **order.to_dict())

        return is_trusted, status, filtered_value, weight

    def get_effective_state(
        self, metric_type: str, timestamp: Optional[float] = None
    ) -> Tuple[float, float, Optional[MaintenanceOrder]]:
        """
        Calculates weighted average state for a metric type across all sensors.

        Returns:
            effective_value: Weighted blend of sensor readings + synthetic fallback
            effective_weight: W̄ = sum of sensor weights (0.0 to 1.0+), NOT including synthetic
            maintenance_order: If effective_weight (W̄) < SOFT_WEIGHT_THRESHOLD
        """
        if timestamp is None:
            timestamp = time.time()

        # Collect sensors of this metric type
        relevant_sensors = [
            (sid, p) for sid, p in self.sensors.items() if p.metric_type == metric_type
        ]

        if not relevant_sensors:
            # No sensors of this type - pure synthetic
            synthetic_val = 0.0
            if self.sensors:
                any_profile = next(iter(self.sensors.values()))
                if any_profile.synthetic_provider:
                    synthetic_val = any_profile.synthetic_provider.get_fallback_reading(
                        metric_type, timestamp
                    )
            return synthetic_val, 0.0, None

        # Weighted average of sensor FILTERED readings (Kalman state)
        weighted_sum = 0.0
        sensor_weight_sum = 0.0  # This is W̄ - sum of sensor weights only
        for sid, profile in relevant_sensors:
            if profile.values:
                latest_val = profile.kalman.x  # Use Kalman filtered state, not raw reading
                w = profile.last_weight
                weighted_sum += w * latest_val
                sensor_weight_sum += w

        # Synthetic fallback contribution: (1 - W̄) * X_synthetic
        synthetic_val = 0.0
        synthetic_provider = relevant_sensors[0][1].synthetic_provider
        if synthetic_provider and synthetic_provider.has_baseline(metric_type):
            synthetic_val = synthetic_provider.get_fallback_reading(metric_type, timestamp)

        synthetic_weight = max(0.0, 1.0 - sensor_weight_sum)
        weighted_sum += synthetic_weight * synthetic_val

        # Total denominator for averaging
        total_denom = sensor_weight_sum + synthetic_weight

        if total_denom == 0:
            return 0.0, 0.0, None

        effective_value = weighted_sum / total_denom
        effective_weight = sensor_weight_sum  # W̄ - only sensor trust, not synthetic

        # Check for critical system degradation (W̄ < threshold)
        maintenance_order = None
        if effective_weight < self.SOFT_WEIGHT_THRESHOLD and synthetic_provider:
            maintenance_order = MaintenanceOrder(
                node_id=self.node_id,
                sensor_id=f"cluster:{metric_type}",
                status="CLUSTER_DEGRADED",
                synthetic_fallback=True,
                anomaly_score=0.0,
                weight=effective_weight,
                timestamp=timestamp,
                details=f"Cluster {metric_type} effective weight {effective_weight:.3f} below threshold. Synthetic fallback dominant.",
            )
            self.maintenance_orders.append(maintenance_order)
            logger.warning("cluster_degraded", **maintenance_order.to_dict())

        return effective_value, effective_weight, maintenance_order

    def get_pending_maintenance(self) -> List[Dict]:
        """Returns all pending maintenance orders as dicts."""
        return [o.to_dict() for o in self.maintenance_orders]

    def clear_maintenance(self, sensor_id: Optional[str] = None) -> int:
        """Clears maintenance orders (after physical calibration)."""
        if sensor_id is None:
            count = len(self.maintenance_orders)
            self.maintenance_orders.clear()
            return count
        initial = len(self.maintenance_orders)
        self.maintenance_orders = [
            o for o in self.maintenance_orders if o.sensor_id != sensor_id
        ]
        return initial - len(self.maintenance_orders)

    def enter_island_mode(self) -> Dict:
        self.is_island_mode = True
        return {
            "node_id": self.node_id,
            "mode": "ISLAND_AUTARKY",
            "timestamp": time.time(),
            "active_sensors": len(self.sensors),
        }

    def exit_island_mode(self) -> Dict:
        self.is_island_mode = False
        return {
            "node_id": self.node_id,
            "mode": "GLOBAL_CONSENSUS",
            "timestamp": time.time(),
        }

    def local_resource_balance(
        self, needs: Dict[str, float], stocks: Dict[str, float]
    ) -> Dict[str, float]:
        allocation = {}
        total_need = sum(needs.values())
        if total_need == 0:
            return allocation
        total_stock = sum(stocks.values())
        if total_stock == 0:
            return allocation
        for resource, need in needs.items():
            stock = stocks.get(resource, 0.0)
            allocation[resource] = min(need, stock)
        return allocation

    def export_vsm_state(self) -> Dict:
        return {
            "node_id": self.node_id,
            "island_mode": self.is_island_mode,
            "sensors": {
                sid: {
                    "metric_type": p.metric_type,
                    "last_weight": p.last_weight,
                    "last_anomaly_score": p.last_anomaly_score,
                    "samples": len(p.values),
                    "last_update": p.last_update,
                }
                for sid, p in self.sensors.items()
            },
            "maintenance_queue": len(self.maintenance_orders),
            "last_update": time.time(),
        }