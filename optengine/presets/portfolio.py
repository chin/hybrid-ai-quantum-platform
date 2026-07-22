from __future__ import annotations

from optengine.catalog import Catalog
from optengine.formulations.cqm import CQM
from optengine.formulations.qubo import QUBO
from optengine.operations.annealing import Annealing
from optengine.operations.exact import ExactSearch
from optengine.solvers.dimod_cqm_exact import DimodCQMExact
from optengine.solvers.dimod_exact import DimodExact
from optengine.solvers.dwave_local import DWaveLocal


def portfolio_catalog() -> Catalog:
    """Reference catalog for the bounded Portfolio vertical slice."""

    return Catalog(
        formulations=(
            CQM(),
            QUBO(lagrange_multiplier=20.0),
        ),
        operations=(
            ExactSearch(max_variables=18),
            Annealing(
                reads_per_iteration=200,
                num_sweeps=2000,
                iterations=10,
                seed=11,
            ),
        ),
        solvers=(
            DimodCQMExact(),
            DimodExact(),
            DWaveLocal(),
        ),
    )


# Transitional alias. New code should use portfolio_catalog.
portfolio_registry = portfolio_catalog
