from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from optengine.recommendation import Recommendation

if TYPE_CHECKING:
    from optengine.analysis import Analysis, Analyzer
    from optengine.catalog import Catalog
    from optengine.domains.base import Domain
    from optengine.execution import Execution
    from optengine.explainers.base import Explainer
    from optengine.policy.base import Policy
    from optengine.utility.base import Utility
    from optengine.writers.base import RecommendationWriter


@dataclass
class OptEngine:
    """Live execution object that coordinates the invariant stage pattern."""

    domain: Domain
    catalog: Catalog
    analyzer: Analyzer
    utility: Utility
    policy: Policy
    explainer: Explainer
    writer: RecommendationWriter
    recommendation: Recommendation
    requested_strategies: tuple[str, ...] | None = None
    output_dir: Path = field(default_factory=lambda: Path("outputs"))
    render: bool = False
    title: str = "OptEngine :: Runtime"
    run_name: str = "run"
    analysis: Analysis | None = None
    executions: list[Execution] = field(default_factory=list)
    started: bool = False
    completed: bool = False

    def log(self, message: str) -> None:
        self.recommendation.logs.append(message)
