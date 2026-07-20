from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import networkx as nx

from optengine.candidate import Candidate
from optengine.domains.maxcut import MaxCutDomain
from optengine.explainers.default import DefaultExplainer
from optengine.formulations.base import Model
from optengine.formulations.qubo import QUBOFormulation
from optengine.interpretation import QuadraticBinaryInterpretation
from optengine.operations.base import Operation
from optengine.operations.exact import ExactSearchOperation
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.registry import StrategyFactory, StrategyRegistry
from optengine.runner import run
from optengine.solvers.base import Solver
from optengine.solvers.dimod_exact import DimodExactSolver
from optengine.strategy import Strategy
from optengine.writers.json import JsonRecommendationWriter


class FailingSolver(Solver):
    name = "runtime-failure"

    def supports(self, model: Model, operation: Operation) -> bool:
        return True

    def execute(
        self,
        model: Model,
        operation: Operation,
        configuration: Mapping[str, Any],
        budget: Mapping[str, Any],
    ) -> Candidate:
        raise RuntimeError("intentional runtime failure")


def _registry() -> StrategyRegistry:
    registry = StrategyRegistry()
    supports = lambda domain, interpretation: (
        isinstance(domain, MaxCutDomain)
        and isinstance(interpretation, QuadraticBinaryInterpretation)
    )
    registry.register(
        StrategyFactory(
            name="exact",
            supports=supports,
            build=lambda domain, interpretation: Strategy(
                name="exact",
                domain=domain,
                formulation=QUBOFormulation(),
                operation=ExactSearchOperation(),
                solver=DimodExactSolver(),
            ),
        )
    )
    registry.register(
        StrategyFactory(
            name="broken",
            supports=supports,
            build=lambda domain, interpretation: Strategy(
                name="broken",
                domain=domain,
                formulation=QUBOFormulation(),
                operation=ExactSearchOperation(),
                solver=FailingSolver(),
            ),
        )
    )
    return registry


def test_runtime_failure_is_recorded_without_corrupting_success(tmp_path: Path):
    graph = nx.cycle_graph(4)

    recommendation = run(
        graph,
        domain=MaxCutDomain(),
        registry=_registry(),
        requested_strategies=("broken", "exact"),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        output_dir=tmp_path,
        run_name="failure-isolation",
    )

    assert [item.strategy for item in recommendation.evaluations] == ["exact"]
    assert recommendation.failures == [
        {
            "strategy": "broken",
            "error_type": "RuntimeError",
            "message": "intentional runtime failure",
        }
    ]
    assert recommendation.decision is not None
    assert recommendation.explanation is not None
    assert recommendation.output_path is not None
    assert Path(recommendation.output_path).exists()
    assert any("Strategy failed: broken" in line for line in recommendation.logs)
