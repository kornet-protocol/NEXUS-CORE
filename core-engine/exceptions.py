# =====================================================================
# NEXUS KORNET ENGINE: EXCEPTIONS v0.2
# Structured error handling for production
# =====================================================================

from __future__ import annotations


class NexusError(Exception):
    """Base exception for NEXUS Core."""

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR") -> None:
        super().__init__(message)
        self.code = code


class VerificationError(NexusError):
    """Zero-knowledge or hardware verification failed."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="VERIFICATION_FAILED")


class ConsensusError(NexusError):
    """Mesh consensus confidence below threshold."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONSENSUS_THRESHOLD")


class DisputeError(NexusError):
    """Dispute arbiter operation failed."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="DISPUTE_ERROR")


class PersistenceError(NexusError):
    """Database persistence layer failed."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="PERSISTENCE_ERROR")


class ConfigurationError(NexusError):
    """Invalid configuration or missing environment variables."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFIG_ERROR")
