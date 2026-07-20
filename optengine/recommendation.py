from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.evaluation import Evaluation
from optengine.explanation import Explanation
from optengine.utility.base import UtilityAssessment


@dataclass
class Recommendation:
    """Persistent result assembled during one OptEngine execution."""

    run_id: str
    input_summary: dict[str, Any] = field(default_factory=dict)
    analysis: Analysis | None = None
    evaluations: list[Evaluation] = field(default_factory=list)
    utility_assessment: UtilityAssessment | None = None
    decision: Decision | None = None
    explanation: Explanation | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    started_at: str | None = None
    completed_at: str | None = None
    output_path: str | None = None
