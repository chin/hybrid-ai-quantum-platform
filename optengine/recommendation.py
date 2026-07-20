from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.evaluation import Evaluation
from optengine.explanation import Explanation


@dataclass
class Recommendation:
    """Persistent result assembled during one OptEngine run."""

    run_id: str
    input_summary: dict[str, Any] = field(default_factory=dict)
    analysis: Analysis | None = None
    evaluations: list[Evaluation] = field(default_factory=list)
    decision: Decision | None = None
    explanation: Explanation | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    output_path: str | None = None
