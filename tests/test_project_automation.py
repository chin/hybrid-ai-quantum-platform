from __future__ import annotations

from datetime import date
from pathlib import Path

from tools.sync_project_fields import _current_iteration


def test_selects_iteration_containing_today() -> None:
    field = {
        "configuration": {
            "iterations": [
                {
                    "id": "current",
                    "title": "Current",
                    "startDate": "2026-07-20",
                    "duration": 14,
                },
                {
                    "id": "next",
                    "title": "Next",
                    "startDate": "2026-08-03",
                    "duration": 14,
                },
            ]
        }
    }
    assert _current_iteration(field, date(2026, 7, 21)) == "current"
    assert _current_iteration(field, date(2026, 8, 3)) == "next"
    assert _current_iteration(field, date(2026, 9, 1)) is None


def test_ci_runs_contract_coverage_and_reference_smoke_tests() -> None:
    workflow = (
        Path(__file__).parents[1] / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")

    assert "tools/dev.py contract-coverage" in workflow
    assert "demos/quickstart.py" in workflow
    assert "demos/portfolio_vertical_slice.py" in workflow


def test_release_workflow_remains_manual_only() -> None:
    workflow = (
        Path(__file__).parents[1] / ".github" / "workflows" / "release.yml"
    ).read_text(encoding="utf-8")

    trigger = workflow.split("permissions:", 1)[0]
    assert "workflow_dispatch:" in trigger
    assert "push:" not in trigger
