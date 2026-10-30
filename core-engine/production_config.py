# =====================================================================
# NEXUS KORNET ENGINE: PRODUCTION CONFIG v0.2
# Environment-aware configuration with validation
# =====================================================================

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

try:
    from .config import (
        CATEGORY_WEIGHTS,
        CATEGORY_LAMBDAS,
        CONFIDENCE_THRESHOLD,
        MIN_WITNESSES,
        CHALLENGE_WINDOW_DAYS,
    )
except ImportError:
    from config import (
        CATEGORY_WEIGHTS,
        CATEGORY_LAMBDAS,
        CONFIDENCE_THRESHOLD,
        MIN_WITNESSES,
        CHALLENGE_WINDOW_DAYS,
    )


@dataclass
class ProductionConfig:
    environment: str = "development"
    db_path: str = "nexus_state.db"
    log_level: str = "INFO"
    enable_persistence: bool = True
    enable_mesh_consensus: bool = False
    zk_verifier_url: Optional[str] = None
    hardware_attestation_endpoint: Optional[str] = None
    validator_api_endpoint: Optional[str] = None
    treasury_multisig_address: Optional[str] = None

    def __post_init__(self) -> None:
        env = os.getenv("NEXUS_ENV", self.environment).lower()
        if env not in ("development", "staging", "production"):
            raise ValueError(f"Invalid NEXUS_ENV: {env}")
        self.environment = env

        if self.environment == "production":
            self.log_level = os.getenv("NEXUS_LOG_LEVEL", "WARNING")
            self.enable_persistence = True
            self.enable_mesh_consensus = True
        elif self.environment == "staging":
            self.log_level = os.getenv("NEXUS_LOG_LEVEL", "INFO")
            self.enable_persistence = True
        else:
            self.log_level = os.getenv("NEXUS_LOG_LEVEL", "DEBUG")
            self.enable_persistence = os.getenv("NEXUS_PERSISTENCE", "false").lower() == "true"

        self.db_path = os.getenv("NEXUS_DB_PATH", self.db_path)
        self.zk_verifier_url = os.getenv("NEXUS_ZK_VERIFIER_URL")
        self.hardware_attestation_endpoint = os.getenv("NEXUS_HARDWARE_ENDPOINT")
        self.validator_api_endpoint = os.getenv("NEXUS_VALIDATOR_API")
        self.treasury_multisig_address = os.getenv("NEXUS_TREASURY_MSIG")

        self._validate()

    def _validate(self) -> None:
        if self.environment == "production":
            missing = []
            if not self.zk_verifier_url:
                missing.append("NEXUS_ZK_VERIFIER_URL")
            if not self.hardware_attestation_endpoint:
                missing.append("NEXUS_HARDWARE_ENDPOINT")
            if not self.validator_api_endpoint:
                missing.append("NEXUS_VALIDATOR_API")
            if not self.treasury_multisig_address:
                missing.append("NEXUS_TREASURY_MSIG")
            if missing:
                raise EnvironmentError(
                    f"Production environment requires: {', '.join(missing)}"
                )

        if self.enable_persistence and not self.db_path:
            raise ValueError("db_path must be set when persistence is enabled")

        if CONFIDENCE_THRESHOLD < 0.0 or CONFIDENCE_THRESHOLD > 1.0:
            raise ValueError(f"CONFIDENCE_THRESHOLD must be in [0,1], got {CONFIDENCE_THRESHOLD}")

        if MIN_WITNESSES < 1:
            raise ValueError(f"MIN_WITNESSES must be >= 1, got {MIN_WITNESSES}")

        if CHALLENGE_WINDOW_DAYS < 1:
            raise ValueError(f"CHALLENGE_WINDOW_DAYS must be >= 1, got {CHALLENGE_WINDOW_DAYS}")

        for category, weight in CATEGORY_WEIGHTS.items():
            if weight < 0:
                raise ValueError(f"Category weight for {category} must be non-negative")

        for category, lam in CATEGORY_LAMBDAS.items():
            if lam < 0:
                raise ValueError(f"Decay lambda for {category} must be non-negative")
