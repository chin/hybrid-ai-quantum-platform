from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Hashable, Literal, Mapping


@dataclass(frozen=True, kw_only=True)
class Interpretation:
    """A domain interpretation of one input."""

    domain: str
    summary: Mapping[str, Any]
    capabilities: frozenset[str] = frozenset()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class QuadraticBinaryInterpretation(Interpretation):
    """A domain-neutral quadratic objective over binary variables."""

    variables: tuple[Hashable, ...]
    linear: Mapping[Hashable, float]
    quadratic: Mapping[tuple[Hashable, Hashable], float]
    offset: float = 0.0
    objective_sense: Literal["minimize", "maximize"] = "minimize"
    domain_data: Any = field(default=None, repr=False, compare=False)
