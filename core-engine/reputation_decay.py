# =====================================================================
# NEXUS KORNET ENGINE: REPUTATION DECAY MODEL v0.2
# Mathematical Model: R_i(t) = sum_k Omega_k * V_k * exp(-lambda_k * (t - t_k)) * (1 - Gini(C_k))
# Thermodynamics: dR/dt = UsefulContribution(t) - lambda * R(t)
# High-Water Mark (HWM): Immutable peak reputation ledger — HWM = max(R(t)) over lifetime
# =====================================================================

import math
from dataclasses import dataclass
from typing import List, Dict, Any

try:
    from .config import CATEGORY_WEIGHTS, CATEGORY_LAMBDAS, CASTE_LAMBDAS, DEFAULT_LAMBDA
    from .logging import get_logger
except ImportError:
    from config import CATEGORY_WEIGHTS, CATEGORY_LAMBDAS, CASTE_LAMBDAS, DEFAULT_LAMBDA
    from logging import get_logger

logger = get_logger("reputation_decay")


@dataclass
class ReputationState:
    """Dual-ledger reputation: Kinetic (decaying) + High-Water Mark (immutable)"""
    kinetic: float          # R(t) — current resource allocation capacity
    high_water_mark: float  # HWM — peak reputation ever achieved, never decays
    last_updated: float     # timestamp of last kinetic update

    @property
    def is_legendary(self) -> bool:
        """HWM exceeds threshold for Hall of Memory inclusion"""
        return self.high_water_mark >= 1000.0  # life_saved threshold


def calculate_reputation(contributions: List[Dict[str, Any]], current_time: float, caste: str = "default", synthesis_multiplier: float = 1.0) -> float:
    if not isinstance(contributions, list):
        raise TypeError("contributions must be a list")
    if current_time < 0:
        raise ValueError("current_time must be non-negative")
    if synthesis_multiplier < 0:
        raise ValueError("synthesis_multiplier must be non-negative")

    lam = CASTE_LAMBDAS.get(caste, DEFAULT_LAMBDA)
    total = 0.0
    for c in contributions:
        omega = CATEGORY_WEIGHTS.get(c.get("type", "tree_planted"), 1.0)
        V = max(0.0, min(1.0, c.get("verification_score", 0.0)))
        category_lambda = CATEGORY_LAMBDAS.get(c.get("type", "tree_planted"), lam)
        t_k = c.get("timestamp", current_time)
        if t_k > current_time:
            logger.warning("future_contribution_skipped", timestamp=t_k, current_time=current_time)
            continue
        decay = math.exp(-category_lambda * (current_time - t_k))
        gini = max(0.0, min(1.0, c.get("gini_coefficient", 0.0)))
        total += omega * V * decay * (1.0 - gini)
    return total * synthesis_multiplier


def update_reputation_state(
    current_state: ReputationState,
    new_kinetic: float,
    current_time: float
) -> ReputationState:
    """
    Update dual-ledger reputation.
    Kinetic decays per thermodynamics. HWM only increases, never decreases.
    """
    new_hwm = max(current_state.high_water_mark, new_kinetic)
    return ReputationState(
        kinetic=new_kinetic,
        high_water_mark=new_hwm,
        last_updated=current_time
    )


def differential_equation(R: float, useful_contribution: float, lambda_decay: float) -> float:
    if R < 0:
        raise ValueError("R must be non-negative")
    if useful_contribution < 0:
        raise ValueError("useful_contribution must be non-negative")
    if lambda_decay < 0:
        raise ValueError("lambda_decay must be non-negative")
    return useful_contribution - lambda_decay * R


def compute_creative_sports_balance(contributions: List[Dict[str, Any]]) -> Dict[str, float]:
    if not isinstance(contributions, list):
        raise TypeError("contributions must be a list")
    creative = sum(c.get("impact", 0.0) for c in contributions if c.get("type") in ("art_created", "scientific_breakthrough", "open_source_contribution"))
    sports = sum(c.get("impact", 0.0) for c in contributions if c.get("type") == "sports_achievement")
    utilitarian = sum(c.get("impact", 0.0) for c in contributions if c.get("type") not in ("art_created", "sports_achievement", "scientific_breakthrough", "open_source_contribution"))
    total = creative + sports + utilitarian
    if total == 0:
        return {"creative": 0.0, "sports": 0.0, "utilitarian": 0.0}
    return {
        "creative": creative / total,
        "sports": sports / total,
        "utilitarian": utilitarian / total,
    }


def get_hall_of_memory_threshold() -> float:
    """Minimum HWM for permanent Hall of Memory inscription"""
    return CATEGORY_WEIGHTS.get("life_saved", 1000.0)
