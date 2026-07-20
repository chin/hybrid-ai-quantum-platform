from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, kw_only=True)
class StrategySummary:
    name: str
    domain: str
    formulation: str
    operation: str
    solver: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class Analysis:
    interpretation: Mapping[str, Any]
    strategies: tuple[StrategySummary, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)
