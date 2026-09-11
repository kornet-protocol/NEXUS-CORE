# =====================================================================
# NEXUS KORNET ENGINE: LOGGING v0.2
# Structured logging for production observability
# =====================================================================

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class NexusLogger:
    def __init__(self, name: str = "nexus", level: str = "INFO") -> None:
        self.name = name
        self.level = level.upper()
        self._levels = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}

    def _should_log(self, level: str) -> bool:
        return self._levels.get(level, 0) >= self._levels.get(self.level, 0)

    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        if not self._should_log(level):
            return
        entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
        }
        entry.update(kwargs)
        print(json.dumps(entry, ensure_ascii=False), file=sys.stderr if level in ("ERROR", "CRITICAL") else sys.stdout)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self._log("CRITICAL", message, **kwargs)


_logger_cache: Optional[NexusLogger] = None


def get_logger(name: str = "nexus") -> NexusLogger:
    global _logger_cache
    if _logger_cache is None:
        level = os.getenv("NEXUS_LOG_LEVEL", "INFO")
        _logger_cache = NexusLogger(name=name, level=level)
    return _logger_cache
