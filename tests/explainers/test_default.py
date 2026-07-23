from __future__ import annotations

import json
from pathlib import Path

import pytest

from optengine.analysis import Analyzer
from optengine.catalog import Catalog
from optengine.execution import ExecutionInstance
from optengine.explainers.default import DefaultExplainer
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.runner import run
from optengine.utility.operational import OperationalUtility
from optengine.writers.json import JsonRecommendationWriter
from tests.support import (
    ExampleDomain,
    ExampleFormulation,
    ExampleOperation,
    ExampleSolver,
)


def _catalog() -> Catalog:
    return Catalog(
        formulations=(ExampleFormulation(),),
        operations=(ExampleOperation(limit=2),),
        solvers=(
            ExampleSolver(
                name="reference",
                reference_flag=True,
                expected_improvement=0.0,
            ),
            ExampleSolver(
                name="candidate",
                values={"x": 0, "y": 1},
                expected_improvement=0.1,
                cost=0.01,
            ),
            ExampleSolver(
                name="failed",
                fail=True,
            ),
        ),
    )


def test_full_stage_workflow_retains_failures_and_writes_artifact(
    tmp_path: Path,
) -> None:
    recommendation = run(
        ExampleDomain(name="workflow"),
        catalog=_catalog(),
        analyzer=Analyzer(),
        utility=OperationalUtility(),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        output_dir=tmp_path,
        run_name="workflow",
    )

    assert recommendation.analysis is not None
    assert len(recommendation.analysis.strategies) == 3
    assert len(recommendation.executions) == 3
    assert sum(item.succeeded for item in recommendation.executions) == 2
    assert sum(item.failed for item in recommendation.executions) == 1
    assert len(recommendation.evaluations) == 2
    assert recommendation.failures[0]["strategy"].endswith(":failed")
    assert recommendation.assessment is not None
    assert recommendation.decision is not None
    assert recommendation.explanation is not None
    assert recommendation.output_path is not None
    assert Path(recommendation.output_path).exists()

    assert recommendation.logs[0] == "OptEngine started."
    assert "Analysis started." in recommendation.logs
    assert "Evaluation started." in recommendation.logs
    assert "Decision started." in recommendation.logs
    assert "Explanation started." in recommendation.logs
    assert "OptEngine finished." in recommendation.logs
    assert recommendation.logs[-1].startswith("Write completed:")

    payload = json.loads(Path(recommendation.output_path).read_text())
    assert payload["domain"]["name"] == "workflow"
    assert payload["analysis"]["fingerprint"]
    assert len(payload["executions"]) == 3
    assert payload["assessment"]["feasible"] is True
    assert payload["decision"]["action"] in {
        "stop",
        "switch",
        "scale",
    }
    assert "utility_assessment" not in payload
    assert payload["failures"][0]["error_type"] == "RuntimeError"

    # Recommendation serialization is explicit and idempotent.
    first = recommendation.to_dict()
    second = recommendation.to_dict()
    assert first == second
    assert recommendation.input_summary == recommendation.domain_summary
    assert recommendation.utility_assessment is recommendation.assessment


def test_requested_strategy_runs_only_that_strategy(
    tmp_path: Path,
) -> None:
    requested = ("example:example-formulation:example-operation:candidate",)
    recommendation = run(
        ExampleDomain(),
        catalog=_catalog(),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        requested_strategies=requested,
        output_dir=tmp_path,
    )
    assert recommendation.analysis is not None
    assert recommendation.analysis.strategy_names == requested
    assert len(recommendation.executions) == 1


def test_execution_instance_delegates_to_public_runner(
    tmp_path: Path,
) -> None:
    instance = ExecutionInstance(
        name="instance",
        domain=ExampleDomain(),
        catalog=_catalog(),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        utility=OperationalUtility(),
        analyzer=Analyzer(),
        requested_strategies=(
            "example:example-formulation:example-operation:reference",
        ),
        output_dir=tmp_path,
        render=False,
        metadata={"ticket": "PR"},
    )
    recommendation = instance.execute()
    assert recommendation.output_path is not None
    assert Path(recommendation.output_path).name.startswith("instance_")


def test_runner_rejects_non_domain_and_writer_rejects_empty_name(
    tmp_path: Path,
) -> None:
    with pytest.raises(TypeError, match="Domain aggregate"):
        run(
            object(),
            catalog=_catalog(),
            policy=ChintropicStopPolicy(),
            explainer=DefaultExplainer(),
            writer=JsonRecommendationWriter(),
            output_dir=tmp_path,
        )

    recommendation = run(
        ExampleDomain(),
        catalog=_catalog(),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        requested_strategies=(
            "example:example-formulation:example-operation:reference",
        ),
        output_dir=tmp_path,
        run_name="valid",
    )
    with pytest.raises(ValueError, match="run_name"):
        JsonRecommendationWriter().write(
            recommendation,
            tmp_path,
            " ",
        )


def test_rendered_workflow_exposes_each_stage(
    tmp_path: Path,
    capsys,
) -> None:
    run(
        ExampleDomain(),
        catalog=_catalog(),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        requested_strategies=(
            "example:example-formulation:example-operation:reference",
        ),
        output_dir=tmp_path,
        render=True,
        title="OptEngine :: Test",
    )
    output = capsys.readouterr().out
    expected = (
        "Problem",
        "  Domain          Example :: example",
        "  Interpretation  ExampleDomain → Objective",
        "  Objective       maximize Objective",
        "  Expression      x + 2·y",
        "Strategy plan (1)",
        "Strategy 1/1",
        "  Formulation     Example Formulation",
        "  Operation       Example Operation",
        "  Solver          Reference • reference",
        "  … Running Reference ...",
        "  ✓ Execution complete",
        "Utility ranking",
        "Recommendation",
        "  Decision        STOP",
        "  Why",
        "Artifact",
        "  Output",
    )
    positions = [output.index(marker) for marker in expected]
    assert positions == sorted(positions)
    assert "{'fingerprint':" not in output
    assert "'strategy':" not in output
