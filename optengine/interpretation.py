from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Hashable, Literal, Mapping


@dataclass(frozen=True, kw_only=True)
class Interpretation:
    """Live domain interpretation of the original input."""

    domain: str
    summary: Mapping[str, Any]
    capabilities: frozenset[str] = frozenset()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class QuadraticBinaryInterpretation(Interpretation):
    """Domain-neutral quadratic binary objective."""

    variables: tuple[Hashable, ...]
    linear: Mapping[Hashable, float]
    quadratic: Mapping[tuple[Hashable, Hashable], float]
    offset: float = 0.0
    objective_sense: Literal["minimize", "maximize"] = "minimize"
    domain_data: Any = None
