# =====================================================================
# NEXUS KORNET ENGINE: GRACEFUL DEGRADATION MODULE v0.1
# Stafford Beer's Viable System Model + Kalman Filter + Island Mode
# =====================================================================

import math
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional, Tuple


@dataclass
class TelemetryReading:
    sensor_id: str
    timestamp: float
    value: float
    raw_payload: bytes
    hardware_signature: Optional[str] = None


@dataclass
class BaselineProfile:
    sensor_id: str
    window_size: int = 100
    values: Deque[float] = field(default_factory=deque)
    timestamps: Deque[float] = field(default_factory=deque)
    mean: float = 0.0
    variance: float = 1.0
    last_update: float = 0.0

    def update(self, value: float, timestamp: float) -> None:
        self.values.append(value)
        self.timestamps.append(timestamp)
        if len(self.values) > self.window_size:
            self.values.popleft()
            self.timestamps.popleft()
        if self.values:
            self.mean = sum(self.values) / len(self.values)
            self.variance = sum((v - self.mean) ** 2 for v in self.values) / max(1, len(self.values) - 1)
        self.last_update = timestamp

    def is_anomaly(self, value: float, threshold_sigma: float = 3.0) -> bool:
        if not self.values or self.variance == 0:
            return False
        z_score = abs(value - self.mean) / math.sqrt(self.variance)
        return z_score > threshold_sigma

    def extrapolate(self, timestamp: float) -> float:
        if len(self.values) < 2:
            return self.mean
        n = len(self.values)
        x = list(range(n))
        y = list(self.values)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        denom = n * sum_x2 - sum_x * sum_x
        if denom == 0:
            return self.mean
        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n
        return slope * n + intercept


class KalmanFilter:
    def __init__(self, process_variance: float = 1e-4, measurement_variance: float = 1e-2):
        self.x = 0.0
        self.p = 1.0
        self.q = process_variance
        self.r = measurement_variance

    def update(self, measurement: float) -> float:
        self.p += self.q
        k = self.p / (self.p + self.r)
        self.x = self.x + k * (measurement - self.x)
        self.p = (1 - k) * self.p
        return self.x


class ViableSystemModel:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.baselines: Dict[str, BaselineProfile] = {}
        self.kalman_filters: Dict[str, KalmanFilter] = {}
        self.is_island_mode: bool = False
        self.local_consensus_round: int = 0

    def ingest_telemetry(self, reading: TelemetryReading) -> Tuple[bool, str, float]:
        profile = self.baselines.setdefault(reading.sensor_id, BaselineProfile(sensor_id=reading.sensor_id))
        kalman = self.kalman_filters.setdefault(reading.sensor_id, KalmanFilter())

        if profile.is_anomaly(reading.value):
            filtered_value = kalman.update(profile.extrapolate(reading.timestamp))
            return False, "ANOMALY_FILTERED", filtered_value

        kalman.update(reading.value)
        profile.update(reading.value, reading.timestamp)
        return True, "ACCEPTED", reading.value

    def enter_island_mode(self) -> Dict:
        self.is_island_mode = True
        return {
            "node_id": self.node_id,
            "mode": "ISLAND_AUTARKY",
            "timestamp": time.time(),
            "active_baselines": len(self.baselines),
        }

    def exit_island_mode(self) -> Dict:
        self.is_island_mode = False
        return {
            "node_id": self.node_id,
            "mode": "GLOBAL_CONSENSUS",
            "timestamp": time.time(),
        }

    def local_resource_balance(self, needs: Dict[str, float], stocks: Dict[str, float]) -> Dict[str, float]:
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
            "baselines": {
                sid: {
                    "mean": bp.mean,
                    "variance": bp.variance,
                    "samples": len(bp.values),
                }
                for sid, bp in self.baselines.items()
            },
            "last_update": time.time(),
        }
