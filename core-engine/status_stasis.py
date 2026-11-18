"""
NEXUS KORNET ENGINE: STATUS STASIS & RESEARCH ESCROW (v0.4)
Protects long-term scientific/engineering cycles from reputational decay.
Implements:
  - Cross-Domain Diversity via Gini Index
  - Peer Stake Collusion Penalties
  - Dual-Layer Slashing (Stake % + High-Water Mark haircut)
"""

import math
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

try:
    from .logging import get_logger
except ImportError:
    from logging import get_logger

logger = get_logger("nexus.status_stasis")


@dataclass
class PeerStake:
    peer_id: str
    domain: str
    stake_amount: float
    staked_hwm: float


@dataclass
class StasisProject:
    project_id: str
    lead_id: str
    lead_current_r: float
    lead_hwm: float
    duration_sec: float
    start_time: float
    target_milestones: int
    completed_milestones: int = 0
    stakes: List[PeerStake] = field(default_factory=list)
    is_active: bool = True
    is_settled: bool = False


class StatusStasisManager:
    def __init__(
        self,
        min_domains: int = 3,
        max_duration_sec: float = 63_072_000.0,  # 24 months hard-cap
        max_gini_threshold: float = 0.65,
        base_slashing_beta: float = 0.10,  # 10% HWM cut on fraud
    ):
        if min_domains < 1:
            raise ValueError("min_domains must be >= 1")
        if max_duration_sec < 1:
            raise ValueError("max_duration_sec must be >= 1")
        if not (0.0 <= max_gini_threshold <= 1.0):
            raise ValueError("max_gini_threshold must be in [0, 1]")
        if not (0.0 <= base_slashing_beta <= 1.0):
            raise ValueError("base_slashing_beta must be in [0, 1]")

        self.min_domains = min_domains
        self.max_duration_sec = max_duration_sec
        self.max_gini_threshold = max_gini_threshold
        self.base_slashing_beta = base_slashing_beta
        self.projects: Dict[str, StasisProject] = {}

    @staticmethod
    def calculate_domain_gini(stakes: List[PeerStake]) -> float:
        """
        Calculates Gini coefficient across staked domains.
        Returns 0.0 for perfectly equal distribution, approaching 1.0 for monopoly.
        """
        if not stakes:
            return 1.0

        domain_totals: Dict[str, float] = {}
        for s in stakes:
            domain_totals[s.domain] = domain_totals.get(s.domain, 0.0) + s.stake_amount

        values = sorted(domain_totals.values())
        n = len(values)
        if n <= 1:
            return 1.0  # Only one domain = complete monopoly

        total = sum(values)
        if total == 0:
            return 1.0

        index_sum = sum((i + 1) * val for i, val in enumerate(values))
        gini = (2.0 * index_sum) / (n * total) - (n + 1.0) / n
        return max(0.0, min(1.0, gini))

    def apply_stasis(
        self,
        project_id: str,
        lead_id: str,
        lead_current_r: float,
        lead_hwm: float,
        duration_sec: float,
        stakes: List[PeerStake],
        target_milestones: int = 1,
    ) -> Tuple[bool, str, float]:
        """
        Validates anti-collusion constraints and freezes reputation decay.
        Returns: (Success: bool, Reason: str, EffectiveLambda: float)
        """
        if not project_id or not lead_id:
            return False, "REJECTED: project_id and lead_id are required.", 1.0
        if lead_current_r < 0 or lead_hwm < 0:
            return False, "REJECTED: lead_current_r and lead_hwm must be non-negative.", 1.0
        if duration_sec <= 0:
            return False, "REJECTED: duration_sec must be positive.", 1.0
        if target_milestones < 1:
            return False, "REJECTED: target_milestones must be >= 1.", 1.0

        # Invariant 1: Max duration cap
        if duration_sec > self.max_duration_sec:
            return False, f"REJECTED: Duration exceeds {self.max_duration_sec}s hard cap.", 1.0

        # Invariant 2: Unique domains count
        unique_domains = {s.domain for s in stakes}
        if len(unique_domains) < self.min_domains:
            return (
                False,
                f"REJECTED: Cross-domain diversity failed. Got {len(unique_domains)} domains, need >={self.min_domains}.",
                1.0,
            )

        # Invariant 3: Gini Domain Monopoly Test
        gini = self.calculate_domain_gini(stakes)
        if gini > self.max_gini_threshold:
            return (
                False,
                f"REJECTED: Domain collusion detected. Gini {gini:.3f} exceeds threshold {self.max_gini_threshold}.",
                1.0,
            )

        total_stake = sum(s.stake_amount for s in stakes)
        if total_stake <= 0:
            return False, "REJECTED: Total stake must be greater than zero.", 1.0

        # Calculate decay dampener: effective_lambda -> 0 as diversity and stakes align
        diversity_factor = 1.0 - gini
        lambda_stasis = max(0.0, 1.0 - diversity_factor)

        self.projects[project_id] = StasisProject(
            project_id=project_id,
            lead_id=lead_id,
            lead_current_r=lead_current_r,
            lead_hwm=lead_hwm,
            duration_sec=duration_sec,
            start_time=time.time(),
            target_milestones=target_milestones,
            stakes=stakes,
            is_active=True,
        )

        logger.info(
            "status_stasis_activated",
            project_id=project_id,
            lead=lead_id,
            effective_lambda=lambda_stasis,
            domains=list(unique_domains),
            gini=gini,
        )

        return True, "STASIS_GRANTED", lambda_stasis

    def settle_project(
        self,
        project_id: str,
        is_fraud_or_abandoned: bool,
        milestone_completion_ratio: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Settles an escrowed project.
        On Fraud: Slashes peer stakes + Haircuts HWM of both lead and cartel backers.
        On Success: Returns stakes + unlocks Synthesis Bonus delta.
        """
        if project_id not in self.projects:
            raise KeyError(f"Project {project_id} not found in stasis registry.")

        project = self.projects[project_id]
        if project.is_settled:
            raise ValueError(f"Project {project_id} already settled.")

        project.is_active = False
        project.is_settled = True

        if is_fraud_or_abandoned or milestone_completion_ratio < 0.2:
            return self._execute_slashing(project)

        return self._execute_success_distribution(project, milestone_completion_ratio)

    def _execute_slashing(self, project: StasisProject) -> Dict[str, Any]:
        """
        Executes progressive slashing against project backers and project lead.
        """
        gini = self.calculate_domain_gini(project.stakes)
        collusion_index = max(0.1, gini)  # Higher collusion = steeper slashing penalty
        multiplier = 1.0 + (0.5 * collusion_index)

        slashed_stakes: Dict[str, float] = {}
        slashed_hwms: Dict[str, float] = {}

        # 1. Haircut project lead HWM (double beta for lead)
        lead_hwm_cut = project.lead_hwm * (1.0 - (self.base_slashing_beta * 2.0))

        # 2. Slashing backers
        for p in project.stakes:
            loss = p.stake_amount * multiplier
            slashed_stakes[p.peer_id] = loss
            # HWM haircut for peers who guaranteed a fraudulent project
            slashed_hwms[p.peer_id] = p.staked_hwm * (1.0 - self.base_slashing_beta)

        logger.warning(
            "stasis_fraud_slashed",
            project_id=project.project_id,
            lead_id=project.lead_id,
            collusion_mult=multiplier,
            slashed_peers=list(slashed_stakes.keys()),
        )

        return {
            "status": "SLASHED",
            "lead_id": project.lead_id,
            "new_lead_hwm": lead_hwm_cut,
            "peer_stake_losses": slashed_stakes,
            "peer_hwm_haircuts": slashed_hwms,
        }

    def _execute_success_distribution(
        self, project: StasisProject, ratio: float
    ) -> Dict[str, Any]:
        """
        Returns peer stakes + computes 10% royalty pool for early discovery.
        """
        total_staked = sum(s.stake_amount for s in project.stakes)
        discovery_royalty_pool = total_staked * 0.10 * ratio

        peer_rewards: Dict[str, float] = {}
        for s in project.stakes:
            share = s.stake_amount / total_staked
            peer_rewards[s.peer_id] = s.stake_amount + (discovery_royalty_pool * share)

        logger.info(
            "stasis_success_settled",
            project_id=project.project_id,
            royalty_pool=discovery_royalty_pool,
        )

        return {
            "status": "REWARDED",
            "lead_id": project.lead_id,
            "peer_returns": peer_rewards,
        }

    def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Returns current status of a stasis project without settling."""
        project = self.projects.get(project_id)
        if not project:
            return None
        return {
            "project_id": project.project_id,
            "lead_id": project.lead_id,
            "is_active": project.is_active,
            "is_settled": project.is_settled,
            "elapsed_sec": time.time() - project.start_time,
            "duration_sec": project.duration_sec,
            "completed_milestones": project.completed_milestones,
            "target_milestones": project.target_milestones,
            "num_peers": len(project.stakes),
            "domains": list({s.domain for s in project.stakes}),
        }