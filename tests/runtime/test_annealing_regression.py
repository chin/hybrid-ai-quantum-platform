from __future__ import annotations

import networkx as nx

from optengine.domains.maxcut import MaxCutDomain
from optengine.formulations.qubo import QUBOFormulation
from optengine.operations.annealing import AnnealingOperation
from optengine.solvers.dwave_local import DWaveLocalSolver


def _execute():
    interpretation = MaxCutDomain().interpret_input(nx.cycle_graph(4))
    model = QUBOFormulation().build(interpretation, {})
    operation = AnnealingOperation(reads_per_iteration=20, num_sweeps=100, seed=17)
    return DWaveLocalSolver().execute(
        model=model,
        operation=operation,
        configuration={},
        budget={"iterations": 2},
    )


def test_seeded_local_annealing_is_reproducible_and_instrumented():
    first = _execute()
    second = _execute()
    assert first.values == second.values
    assert first.native_score == second.native_score
    assert first.native_metrics["iterations"] == 2
    assert first.native_metrics["total_reads"] == 40
    assert len(first.native_metrics["history"]) == 2
    assert first.provenance["library"] == "dwave-samplers"
