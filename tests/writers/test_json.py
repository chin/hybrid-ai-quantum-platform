from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

import numpy as np
import pytest

from optengine.candidate import Candidate
from optengine.decision import Decision
from optengine.evaluation import Evaluation
from optengine.explanation import Explanation
from optengine.recommendation import Recommendation
from optengine.writers.json import (
    JsonRecommendationWriter,
    _json_safe,
)


class ExampleEnum(Enum):
    VALUE = "value"


def build_recommendation() -> Recommendation:
    candidate = Candidate(
        strategy="exact",
        formulation="qubo",
        operation="exact-search",
        solver="dimod-exact",
        values={"sample": {0: np.int8(0), 1: np.int8(1)}},
        native_score=np.float64(-1.0),
        status="complete",
        metadata={},
        provenance={},
    )
    evaluation = Evaluation(
        strategy="exact",
        candidate=candidate,
        feasible=True,
        quality=1.0,
        metrics={"array": np.array([1, 2])},
        policy_evidence={"quality": 1.0},
        provenance={},
    )
    return Recommendation(
        run_id="writer-test",
        evaluations=[evaluation],
        decision=Decision(
            action="stop",
            selected_strategy="exact",
            reason_code="TEST",
        ),
        explanation=Explanation(
            summary="Complete.",
            selected_strategy="exact",
        ),
        provenance={
            "path": Path("example"),
            "enum": ExampleEnum.VALUE,
            "set": {1, 2},
        },
        logs=[
            "OptEngine started.",
            "OptEngine finished.",
        ],
    )


def test_writer_creates_valid_complete_json(
    tmp_path: Path,
) -> None:
    recommendation = build_recommendation()

    path = JsonRecommendationWriter().write(
        recommendation,
        tmp_path,
        "writer",
    )

    payload = json.loads(path.read_text(encoding="utf-8"))

    assert path.exists()
    assert path.name.startswith("writer_")
    assert path.read_text(encoding="utf-8").endswith("\n")
    assert payload["output_path"] == str(path)
    assert payload["logs"][-1] == "OptEngine finished."
    assert payload["evaluations"][0]["candidate"]["values"]["sample"] == {
        "0": 0,
        "1": 1,
    }


def test_json_safe_converts_supported_runtime_values() -> None:
    result = _json_safe(
        {
            "integer": np.int8(1),
            "floating": np.float64(1.5),
            "array": np.array([1, 2]),
            "path": Path("example"),
            "enum": ExampleEnum.VALUE,
            "set": {1, 2},
        }
    )

    assert result["integer"] == 1
    assert result["floating"] == 1.5
    assert result["array"] == [1, 2]
    assert result["path"] == "example"
    assert result["enum"] == "value"
    assert sorted(result["set"]) == [1, 2]


def test_json_safe_rejects_unsupported_value() -> None:
    class Unsupported:
        pass

    with pytest.raises(TypeError, match="cannot be serialized"):
        _json_safe(Unsupported())


def test_writer_rejects_nan(
    tmp_path: Path,
) -> None:
    recommendation = build_recommendation()
    recommendation.provenance["bad"] = float("nan")

    with pytest.raises(ValueError):
        JsonRecommendationWriter().write(
            recommendation,
            tmp_path,
            "nan",
        )
