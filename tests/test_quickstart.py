from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

import optengine
from demos.portfolio_vertical_slice import load_instance
from demos.quickstart import (
    build_quickstart_domain,
    build_quickstart_graph,
    build_quickstart_input,
)
from optengine.domains.maxcut import MaxCut
from optengine.domains.portfolio import Portfolio
from optengine.presets.maxcut import (
    maxcut_catalog,
    maxcut_registry,
)
from optengine.presets.portfolio import (
    portfolio_catalog,
    portfolio_registry,
)
from optengine.registry import StrategyRegistry


def test_canonical_public_api_exports() -> None:
    expected = {
        "Domain",
        "MaxCut",
        "Portfolio",
        "Curve",
        "Expression",
        "Objective",
        "Formulation",
        "Model",
        "QUBO",
        "CQM",
        "Operation",
        "ExactSearch",
        "Annealing",
        "Solver",
        "DimodExact",
        "DimodCQMExact",
        "DWaveLocal",
        "Catalog",
        "Analyzer",
        "Analysis",
        "Strategy",
        "Execution",
        "Utility",
        "Assessment",
        "Policy",
        "Stop",
        "Switch",
        "Scale",
        "Recommendation",
        "run",
    }
    assert expected <= set(optengine.__all__)
    assert optengine.MaxCut is MaxCut
    assert optengine.Portfolio is Portfolio


def test_legacy_registry_aliases_point_to_catalog() -> None:
    assert StrategyRegistry is optengine.Catalog
    assert maxcut_registry is maxcut_catalog
    assert portfolio_registry is portfolio_catalog


def test_quickstart_builders_construct_populated_domain_aggregate() -> None:
    graph = build_quickstart_graph()
    assert isinstance(graph, nx.Graph)
    assert build_quickstart_input().edges == graph.edges
    domain = build_quickstart_domain()
    assert isinstance(domain, MaxCut)
    assert domain.domain_type == "max-cut"
    assert domain.summary["vertices"] == 4
    assert not hasattr(domain, "input")


def test_portfolio_demo_configuration_constructs_domain_aggregate(
    tmp_path: Path,
) -> None:
    path = tmp_path / "portfolio.json"
    path.write_text(
        json.dumps(
            {
                "name": "demo",
                "problem": {
                    "assets": ["A", "B"],
                    "expected_returns": [0.1, 0.05],
                    "covariance": [
                        [0.04, 0.01],
                        [0.01, 0.02],
                    ],
                    "allocation_increment": 0.5,
                    "risk_aversion": 1.0,
                },
                "execution": {
                    "strategies": [],
                    "render": False,
                    "output_dir": str(tmp_path / "outputs"),
                },
            }
        )
    )
    instance = load_instance(path)
    assert isinstance(instance.domain, Portfolio)
    assert instance.name == "demo"
    assert instance.requested_strategies is None
    assert instance.metadata["config_path"] == str(path)


def test_presets_are_canonical_catalogs() -> None:
    maxcut = maxcut_catalog()
    portfolio = portfolio_catalog()
    assert maxcut.formulation_names == ("qubo",)
    assert maxcut.operation_names == (
        "exact-search",
        "annealing",
    )
    assert maxcut.solver_names == (
        "dimod-exact",
        "dwave-local",
    )
    assert portfolio.formulation_names == ("cqm", "qubo")
    assert portfolio.operation_names == (
        "exact-search",
        "annealing",
    )
    assert portfolio.solver_names == (
        "dimod-cqm-exact",
        "dimod-exact",
        "dwave-local",
    )
