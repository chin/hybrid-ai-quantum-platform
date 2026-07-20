from __future__ import annotations

from optengine.domains.maxcut import MaxCutDomain
from optengine.formulations.qubo import QUBOFormulation
from optengine.interpretation import QuadraticBinaryInterpretation
from optengine.operations.annealing import AnnealingOperation
from optengine.operations.exact import ExactSearchOperation
from optengine.registry import StrategyFactory, StrategyRegistry
from optengine.solvers.dimod_exact import DimodExactSolver
from optengine.solvers.dwave_local import DWaveLocalSolver
from optengine.strategy import Strategy


def maxcut_registry() -> StrategyRegistry:
    registry = StrategyRegistry()

    registry.register(
        StrategyFactory(
            name="maxcut-exact",
            supports=lambda domain, interpretation: (
                isinstance(domain, MaxCutDomain)
                and isinstance(
                    interpretation,
                    QuadraticBinaryInterpretation,
                )
                and len(interpretation.variables) <= 18
            ),
            build=lambda domain, interpretation: Strategy(
                name="maxcut-exact",
                domain=domain,
                formulation=QUBOFormulation(),
                operation=ExactSearchOperation(),
                solver=DimodExactSolver(),
                metadata={"role": "reference"},
            ),
        )
    )

    registry.register(
        StrategyFactory(
            name="maxcut-local-annealing",
            supports=lambda domain, interpretation: (
                isinstance(domain, MaxCutDomain)
                and isinstance(
                    interpretation,
                    QuadraticBinaryInterpretation,
                )
            ),
            build=lambda domain, interpretation: Strategy(
                name="maxcut-local-annealing",
                domain=domain,
                formulation=QUBOFormulation(),
                operation=AnnealingOperation(
                    reads_per_iteration=100,
                    num_sweeps=1000,
                    seed=7,
                ),
                solver=DWaveLocalSolver(),
                budget={"iterations": 30},
                metadata={"role": "candidate"},
            ),
        )
    )

    return registry
