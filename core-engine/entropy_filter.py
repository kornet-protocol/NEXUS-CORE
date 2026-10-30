# =====================================================================
# NEXUS KORNET ENGINE: ENTROPY FILTER - THERMODYNAMICS OF STATUS v0.1
# dR_i/dt = UsefulContribution(t) - lambda * R_i(t)
# Second Law of Thermodynamics applied to social structures
# =====================================================================

import math
from dataclasses import dataclass
from typing import Dict, List

from .config import CATEGORY_WEIGHTS, CATEGORY_LAMBDAS, DEFAULT_LAMBDA


@dataclass
class ContributionEvent:
    timestamp: float
    category: str
    impact: float
    confidence: float
    decay_lambda: float


class EntropyFilter:
    def __init__(self):
        self.default_lambda = DEFAULT_LAMBDA

    def calculate_reputation(self, contributions: List[ContributionEvent], current_time: float) -> float:
        total = 0.0
        for c in contributions:
            omega = CATEGORY_WEIGHTS.get(c.category, 1.0)
            confidence = max(0.0, min(1.0, c.confidence))
            lam = c.decay_lambda if c.decay_lambda > 0 else CATEGORY_LAMBDAS.get(c.category, self.default_lambda)
            elapsed = current_time - c.timestamp
            decay = math.exp(-lam * elapsed)
            total += omega * confidence * decay
        return total

    def differential_equation(self, R: float, useful_contribution: float, lambda_decay: float) -> float:
        return useful_contribution - lambda_decay * R

    def estimate_lambda(self, category: str) -> float:
        return CATEGORY_LAMBDAS.get(category, self.default_lambda)

    def get_max_reputation(self, category: str) -> float:
        return CATEGORY_WEIGHTS.get(category, 1.0)

    def time_to_half_reputation(self, R: float, lambda_decay: float) -> float:
        if lambda_decay <= 0:
            return float("inf")
        return math.log(2.0) / lambda_decay

    def is_gerontocracy_risk(self, contributions: List[ContributionEvent], current_time: float, threshold_years: float = 5.0) -> bool:
        if not contributions:
            return False
        latest = max(c.timestamp for c in contributions)
        years_since_last = (current_time - latest) / (365.25 * 24 * 3600)
        return years_since_last > threshold_years

    def compute_creative_sports_balance(self, contributions: List[ContributionEvent]) -> Dict[str, float]:
        creative = sum(c.impact for c in contributions if c.category in ("art_created", "scientific_breakthrough", "open_source_contribution"))
        sports = sum(c.impact for c in contributions if c.category == "sports_achievement")
        utilitarian = sum(c.impact for c in contributions if c.category not in ("art_created", "sports_achievement", "scientific_breakthrough", "open_source_contribution"))
        total = creative + sports + utilitarian
        if total == 0:
            return {"creative": 0.0, "sports": 0.0, "utilitarian": 0.0}
        return {
            "creative": creative / total,
            "sports": sports / total,
            "utilitarian": utilitarian / total,
        }
