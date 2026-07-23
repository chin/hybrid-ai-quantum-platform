from __future__ import annotations


import pytest

from optengine.analysis import Analyzer
from optengine.domains.maxcut import MaxCut
from optengine.domains.portfolio import Portfolio
from optengine.formulations.cqm import CQM
from optengine.formulations.qubo import QUBO
from optengine.presets.maxcut import maxcut_catalog
from optengine.presets.portfolio import portfolio_catalog
from optengine.solvers.dimod_cqm_exact import DimodCQMExact
from optengine.solvers.dimod_exact import DimodExact
from optengine.solvers.dwave_local import DWaveLocal


def _maxcut() -> MaxCut:
    a = MaxCut.Vertex(identifier="A")
    b = MaxCut.Vertex(identifier="B")
    c = MaxCut.Vertex(identifier="C")
    return MaxCut(
        name="triangle",
        graph=MaxCut.Graph(
            vertices=(a, b, c),
            edges=(
                MaxCut.Edge(first=a, second=b),
                MaxCut.Edge(first=b, second=c),
                MaxCut.Edge(first=a, second=c),
            ),
        ),
    )


def _portfolio() -> Portfolio:
    return Portfolio.from_mapping(
        {
            "assets": ["Growth", "Income"],
            "expected_returns": [0.12, 0.08],
            "covariance": [
                [0.04, 0.006],
                [0.006, 0.02],
            ],
            "allocation_increment": 0.5,
            "risk_aversion": 1.0,
        }
    )


def test_missing_external_backends_report_unavailable_without_import_failure() -> None:
    # Dependency discovery is local behavior; importing OptEngine never requires
    # optional backend modules to have already loaded.
    assert isinstance(QUBO().available, bool)
    assert isinstance(CQM().available, bool)
    assert isinstance(DimodExact().available, bool)
    assert isinstance(DimodCQMExact().available, bool)
    assert isinstance(DWaveLocal().available, bool)


def test_maxcut_qubo_exact_reference_regression() -> None:
    pytest.importorskip("dimod")

    domain = _maxcut()
    analysis = Analyzer().analyze(
        domain,
        maxcut_catalog(),
        requested=("max-cut:qubo:exact-search:dimod-exact",),
    )
    execution = analysis.strategies[0].execute()
    assert execution.succeeded
    assert execution.evaluation is not None
    assert execution.evaluation.feasible
    assert execution.evaluation.cut_value == 2.0
    assert len(execution.evaluation.cut_edges) == 2


def test_portfolio_cqm_and_qubo_expression_regression() -> None:
    pytest.importorskip("dimod")

    domain = _portfolio()
    cqm = CQM().express(domain.objective)
    qubo = QUBO(lagrange_multiplier=20.0).express(domain.objective)
    assert cqm is not None
    assert qubo is not None
    assert cqm.curve.constrained
    assert not qubo.curve.constrained
    assert qubo.metadata["source"] == "cqm"


def test_portfolio_exact_reference_regression() -> None:
    pytest.importorskip("dimod")

    domain = _portfolio()
    analysis = Analyzer().analyze(
        domain,
        portfolio_catalog(),
        requested=("portfolio:cqm:exact-search:dimod-cqm-exact",),
    )
    execution = analysis.strategies[0].execute()
    assert execution.succeeded
    assert execution.evaluation is not None
    assert execution.evaluation.feasible
    assert execution.evaluation.budget_feasible
    assert execution.evaluation.one_choice_feasible


def test_dwave_local_seeded_regression() -> None:
    pytest.importorskip("dimod")
    pytest.importorskip("dwave.samplers")

    domain = _maxcut()
    catalog = maxcut_catalog()
    analysis = Analyzer().analyze(
        domain,
        catalog,
        requested=("max-cut:qubo:annealing:dwave-local",),
    )
    first = analysis.strategies[0].execute()
    second = analysis.strategies[0].execute()
    assert first.succeeded and second.succeeded
    assert first.candidate is not None
    assert second.candidate is not None
    assert first.candidate.partition.to_dict() == second.candidate.partition.to_dict()
    assert first.evaluation is not None
    assert second.evaluation is not None
    assert first.evaluation.cut_value == second.evaluation.cut_value
