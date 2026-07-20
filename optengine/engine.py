from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from optengine.recommendation import Recommendation

if TYPE_CHECKING:
    from optengine.domains.base import Domain
    from optengine.explainers.base import Explainer
    from optengine.interpretation import Interpretation
    from optengine.policy.base import Policy
    from optengine.registry import StrategyRegistry
    from optengine.strategy import Strategy
    from optengine.utility.base import UtilityModel
    from optengine.writers.base import RecommendationWriter


@dataclass
class OptEngine:
    """Live state and collaborators for one execution."""

    input_data: Any
    domain: Domain
    registry: StrategyRegistry
    utility_model: UtilityModel
    policy: Policy
    explainer: Explainer
    writer: RecommendationWriter
    recommendation: Recommendation
    requested_strategies: tuple[str, ...] | None = None
    output_dir: Path = field(default_factory=lambda: Path("outputs"))
    render: bool = False
    title: str = "OptEngine :: Runtime"
    run_name: str = "run"
    interpretation: Interpretation | None = None
    strategies: list[Strategy] = field(default_factory=list)
    started: bool = False
    completed: bool = False

    def log(self, message: str) -> None:
        self.recommendation.logs.append(message)
