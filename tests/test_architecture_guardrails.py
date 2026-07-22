from __future__ import annotations

import ast
from pathlib import Path

from optengine.domains.portfolio import Portfolio


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    values = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            values.add(node.module)
    return values


def test_engine_and_stages_do_not_import_specific_domains() -> None:
    root = Path(__file__).parents[1]
    paths = [
        root / "optengine" / "engine.py",
        root / "optengine" / "runner.py",
        root / "optengine" / "analysis.py",
        *(root / "optengine" / "stages").glob("*.py"),
    ]
    forbidden = {
        "optengine.domains.maxcut",
        "optengine.domains.portfolio",
    }
    for path in paths:
        assert not (_imports(path) & forbidden), path


def test_domain_is_aggregate_no_portfolio_input_type() -> None:
    import optengine.domains.portfolio as module

    assert not hasattr(module, "PortfolioInput")
    assert "input" not in Portfolio.__dataclass_fields__


def test_capability_request_and_result_are_nested() -> None:
    from optengine.formulations.base import Formulation
    from optengine.operations.base import Operation
    from optengine.solvers.base import Solver

    assert Formulation.Capability.__qualname__.startswith("Formulation.")
    assert Operation.Capability.__qualname__.startswith("Operation.")
    assert Operation.Request.__qualname__.startswith("Operation.")
    assert Solver.Capability.__qualname__.startswith("Solver.")
    assert Solver.Result.__qualname__.startswith("Solver.")
