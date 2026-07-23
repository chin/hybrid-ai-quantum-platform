from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.execution import Execution
from optengine.explanation import Explanation
from optengine.utility.base import Assessment


@dataclass
class Recommendation:
    """Persistent result assembled by one complete OptEngine workflow."""

    run_id: str
    domain_summary: Mapping[str, Any] = field(default_factory=dict)
    analysis: Analysis | None = None
    executions: list[Execution] = field(default_factory=list)
    assessment: Assessment | None = None
    decision: Decision | None = None
    explanation: Explanation | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)
    started_at: str | None = None
    completed_at: str | None = None
    output_path: str | None = None

    @property
    def evaluations(self) -> tuple[Any, ...]:
        """All successfully produced Domain Evaluations."""

        return tuple(
            execution.evaluation
            for execution in self.executions
            if execution.evaluation is not None
        )

    @property
    def failures(self) -> tuple[Mapping[str, Any], ...]:
        """Failure evidence retained from independently isolated executions."""

        return tuple(
            {
                "strategy": execution.strategy.name,
                **(
                    {}
                    if execution.failure is None
                    else dict(execution.failure.to_dict())
                ),
            }
            for execution in self.executions
            if execution.failed
        )

    # Transitional read-only aliases for old integrations. Canonical new names
    # are domain_summary and assessment.
    @property
    def input_summary(self) -> Mapping[str, Any]:
        return self.domain_summary

    @property
    def utility_assessment(self) -> Assessment | None:
        return self.assessment

    def to_dict(self) -> Mapping[str, Any]:
        """Return an explicit, cycle-free artifact representation."""

        return {
            "run_id": self.run_id,
            "domain": dict(self.domain_summary),
            "analysis": (None if self.analysis is None else self.analysis.to_dict()),
            "executions": [execution.to_dict() for execution in self.executions],
            "assessment": (
                None if self.assessment is None else self.assessment.to_dict()
            ),
            "decision": (None if self.decision is None else self.decision.to_dict()),
            "explanation": (
                None if self.explanation is None else self.explanation.to_dict()
            ),
            "provenance": dict(self.provenance),
            "logs": list(self.logs),
            "failures": [dict(failure) for failure in self.failures],
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "output_path": self.output_path,
        }
