from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class StrategySummary:
    name: str
    domain: str
    formulation: str
    operation: str
    solver: str
    metadata: Mapping[str, Any]


@dataclass(frozen=True)
class Analysis:
    interpretation: Mapping[str, Any]
    strategies: tuple[StrategySummary, ...]
