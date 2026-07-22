from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from optengine.identity import fingerprint
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from optengine.analysis import Analyzer
    from optengine.candidate import Candidate
    from optengine.catalog import Catalog
    from optengine.domains.base import Domain
    from optengine.evaluation import Evaluation
    from optengine.explainers.base import Explainer
    from optengine.policy.base import Policy
    from optengine.recommendation import Recommendation
    from optengine.solvers.base import Solver
    from optengine.strategy import Strategy
    from optengine.utility.base import Utility
    from optengine.writers.base import RecommendationWriter


class ExecutionState:
    code: str
    succeeded: bool
    failed: bool


class Pending(ExecutionState):
    code = "pending"
    succeeded = False
    failed = False


class Complete(ExecutionState):
    code = "complete"
    succeeded = True
    failed = False


class Failed(ExecutionState):
    code = "failed"
    succeeded = False
    failed = True


@dataclass(frozen=True, kw_only=True)
class Failure:
    error_type: str
    message: str

    def to_dict(self) -> Mapping[str, str]:
        return {
            "error_type": self.error_type,
            "message": self.message,
        }


@dataclass(frozen=True, kw_only=True)
class Execution:
    """Immutable record of one attempted Strategy."""

    strategy: Strategy
    state: ExecutionState
    result: Solver.Result | None = None
    candidate: Candidate | None = None
    evaluation: Evaluation | None = None
    runtime_s: float | None = None
    failure: Failure | None = None

    @property
    def fingerprint(self) -> str:
        return fingerprint(
            {
                "strategy": self.strategy.fingerprint,
                "status": self.state.code,
                "result": (None if self.result is None else self.result.to_dict()),
                "candidate": (
                    None if self.candidate is None else self.candidate.to_dict()
                ),
                "evaluation": (
                    None if self.evaluation is None else self.evaluation.to_dict()
                ),
                "failure": (None if self.failure is None else self.failure.to_dict()),
            }
        )

    @property
    def succeeded(self) -> bool:
        return self.state.succeeded

    @property
    def failed(self) -> bool:
        return self.state.failed

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "fingerprint": self.fingerprint,
            "strategy": self.strategy.summary(),
            "status": self.state.code,
            "runtime_s": self.runtime_s,
            "result": (None if self.result is None else self.result.to_dict()),
            "candidate": (None if self.candidate is None else self.candidate.to_dict()),
            "evaluation": (
                None if self.evaluation is None else self.evaluation.to_dict()
            ),
            "failure": (None if self.failure is None else self.failure.to_dict()),
        }


@dataclass(frozen=True, kw_only=True)
class ExecutionInstance:
    """Reusable named execution request."""

    name: str
    domain: Domain
    catalog: Catalog
    policy: Policy
    explainer: Explainer
    writer: RecommendationWriter
    utility: Utility | None = None
    analyzer: Analyzer | None = None
    requested_strategies: tuple[str, ...] | None = None
    output_dir: Path = Path("outputs")
    render: bool = True
    title: str = "OptEngine :: Execution"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def execute(self) -> Recommendation:
        from optengine.runner import run

        return run(
            self.domain,
            catalog=self.catalog,
            policy=self.policy,
            explainer=self.explainer,
            writer=self.writer,
            utility=self.utility,
            analyzer=self.analyzer,
            requested_strategies=self.requested_strategies,
            output_dir=self.output_dir,
            render=self.render,
            title=self.title,
            run_name=self.name,
        )
