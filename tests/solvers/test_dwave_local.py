from __future__ import annotations

import networkx as nx
import pytest

import optengine.solvers.dwave_local as solver_module
from optengine.domains.maxcut import MaxCutDomain
from optengine.formulations.qubo import QUBOFormulation
from optengine.operations.annealing import AnnealingOperation
from optengine.operations.exact import ExactSearchOperation
from optengine.solvers.dwave_local import DWaveLocalSolver


def make_model():
    graph = nx.cycle_graph(4)
    nx.set_edge_attributes(graph, 1.0, "weight")
    return QUBOFormulation().build(
        MaxCutDomain().interpret_input(graph),
        {},
    )


def test_supports_qubo_annealing() -> None:
    solver = DWaveLocalSolver()
    model = make_model()

    assert solver.supports(model, AnnealingOperation()) is True
    assert solver.supports(model, ExactSearchOperation()) is False


def test_fixed_seed_produces_repeatable_candidate() -> None:
    solver = DWaveLocalSolver()
    model = make_model()
    operation = AnnealingOperation(
        reads_per_iteration=20,
        num_sweeps=100,
        seed=17,
    )
    budget = {"iterations": 3}

    first = solver.execute(model, operation, {}, budget)
    second = solver.execute(model, operation, {}, budget)

    assert first.values == second.values
    assert first.native_score == second.native_score


def test_history_matches_budget_and_best_energy_never_worsens() -> None:
    candidate = DWaveLocalSolver().execute(
        make_model(),
        AnnealingOperation(
            reads_per_iteration=20,
            num_sweeps=100,
            seed=17,
        ),
        {},
        {"iterations": 4},
    )

    history = candidate.metadata["history"]
    assert len(history) == 4

    best_energies = [
        record["best_so_far_energy"]
        for record in history
    ]
    assert best_energies == sorted(best_energies, reverse=True)
    assert all(
        type(value) is int
        for value in candidate.values["sample"].values()
    )
    assert candidate.runtime_s is not None
    assert candidate.provenance["execution"] == "local"


@pytest.mark.parametrize("iterations", [0, -1])
def test_invalid_iteration_budget_is_rejected(
    iterations: int,
) -> None:
    with pytest.raises(ValueError, match="iterations"):
        DWaveLocalSolver().execute(
            make_model(),
            AnnealingOperation(),
            {},
            {"iterations": iterations},
        )


def test_sampler_failure_propagates_explicitly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingSampler:
        def sample(self, model, **kwargs):
            raise RuntimeError("sampler failed")

    monkeypatch.setattr(
        solver_module,
        "SimulatedAnnealingSampler",
        lambda: FailingSampler(),
    )

    with pytest.raises(RuntimeError, match="sampler failed"):
        DWaveLocalSolver().execute(
            make_model(),
            AnnealingOperation(),
            {},
            {"iterations": 1},
        )
