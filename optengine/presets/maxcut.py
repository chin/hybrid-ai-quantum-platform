from __future__ import annotations

from optengine.catalog import Catalog
from optengine.formulations.qubo import QUBO
from optengine.operations.annealing import Annealing
from optengine.operations.exact import ExactSearch
from optengine.solvers.dimod_exact import DimodExact
from optengine.solvers.dwave_local import DWaveLocal


def maxcut_catalog() -> Catalog:
    """Reference catalog for the Max-Cut vertical slice."""

    return Catalog(
        formulations=(QUBO(),),
        operations=(
            ExactSearch(max_variables=18),
            Annealing(
                reads_per_iteration=100,
                num_sweeps=1000,
                iterations=30,
                seed=7,
            ),
        ),
        solvers=(
            DimodExact(),
            DWaveLocal(),
        ),
    )


# Transitional alias. New code should use maxcut_catalog.
maxcut_registry = maxcut_catalog
