from __future__ import annotations

import pytest

from optengine.analysis import Analyzer, CompatibilityRecord
from optengine.catalog import Catalog
from optengine.compatibility import Compatibility
from optengine.errors import NoCompatibleStrategyError
from optengine.execution import Complete, Failed, Failure, Pending
from tests.support import (
    ExampleDomain,
    ExampleFormulation,
    ExampleOperation,
    ExampleSolver,
    ExplodingFormulation,
    NoneFormulation,
    RejectingFormulation,
)


def _catalog(*solvers: ExampleSolver) -> Catalog:
    return Catalog(
        formulations=(ExampleFormulation(),),
        operations=(ExampleOperation(limit=2),),
        solvers=solvers
        or (
            ExampleSolver(name="first"),
            ExampleSolver(
                name="second",
                values={"x": 0, "y": 1},
            ),
        ),
    )


def test_analyzer_produces_n_strategies_and_records_realtime_compatibility() -> None:
    analysis = Analyzer().analyze(
        ExampleDomain(),
        _catalog(),
    )
    assert analysis.strategy_names == (
        "example:example-formulation:example-operation:first",
        "example:example-formulation:example-operation:second",
    )
    assert analysis.metadata == {
        "formulation_count": 1,
        "operation_count": 1,
        "solver_count": 2,
        "strategy_count": 2,
    }
    assert analysis.fingerprint
    payload = analysis.to_dict()
    assert payload["fingerprint"] == analysis.fingerprint
    assert payload["strategies"][0]["model"]["curve"]["input_count"] == 2
    assert any(
        record.stage == "formulation" and record.supported
        for record in analysis.compatibility
    )
    assert any(
        record.stage == "operation" and record.supported
        for record in analysis.compatibility
    )
    assert (
        sum(
            record.stage == "solver" and record.supported
            for record in analysis.compatibility
        )
        == 2
    )


def test_requested_strategies_filter_and_preserve_requested_order() -> None:
    domain = ExampleDomain()
    catalog = _catalog()
    requested = (
        "example:example-formulation:example-operation:second",
        "example:example-formulation:example-operation:first",
    )
    analysis = Analyzer().analyze(
        domain,
        catalog,
        requested=requested,
    )
    assert analysis.strategy_names == requested

    with pytest.raises(KeyError, match="Unknown or incompatible"):
        Analyzer().analyze(
            domain,
            catalog,
            requested=("missing",),
        )


def test_analyzer_records_rejections_exceptions_and_none_models() -> None:
    catalog = Catalog(
        formulations=(
            RejectingFormulation(),
            ExplodingFormulation(),
            NoneFormulation(),
            ExampleFormulation(),
        ),
        operations=(ExampleOperation(limit=1),),
        solvers=(
            ExampleSolver(
                name="unavailable",
                available_flag=False,
            ),
        ),
    )
    with pytest.raises(NoCompatibleStrategyError):
        Analyzer().analyze(ExampleDomain(), catalog)

    # Rerun individual paths with direct compatibility evidence assertions.
    rejected = RejectingFormulation().compatibility(ExampleDomain().objective)
    assert not rejected

    compatibility_record = CompatibilityRecord.from_result(
        stage="formulation",
        collaborator="rejecting",
        result=Compatibility.rejected("reason", evidence={"x": 1}),
    )
    assert compatibility_record.to_dict() == {
        "stage": "formulation",
        "collaborator": "rejecting",
        "supported": False,
        "reasons": ["reason"],
        "evidence": {"x": 1},
    }


def test_domain_interpretation_type_is_enforced() -> None:
    class BadDomain(ExampleDomain):
        def _interpret_in(self, domain):
            return object()

    with pytest.raises(TypeError, match="Interpretation"):
        Analyzer().analyze(
            BadDomain(),
            _catalog(ExampleSolver()),
        )


def test_strategy_identity_summary_and_successful_execution() -> None:
    analysis = Analyzer().analyze(
        ExampleDomain(offset=1.0),
        _catalog(
            ExampleSolver(
                name="reference",
                reference_flag=True,
            )
        ),
    )
    strategy = analysis.strategies[0]

    assert strategy.reference
    assert strategy.fingerprint == strategy.fingerprint
    summary = strategy.summary()
    assert summary["name"] == strategy.name
    assert summary["reference"] is True
    assert summary["operation_configuration"] == {"limit": 2}

    execution = strategy.execute()
    assert isinstance(execution.state, Complete)
    assert execution.succeeded
    assert not execution.failed
    assert execution.result is not None
    assert execution.candidate is not None
    assert execution.evaluation is not None
    assert execution.evaluation.quality == 4.0
    assert execution.runtime_s is not None
    assert execution.fingerprint
    payload = execution.to_dict()
    assert payload["status"] == "complete"
    assert payload["evaluation"]["quality"] == 4.0


def test_strategy_failure_isolation_for_exception_and_partial_status() -> None:
    exploding = (
        Analyzer()
        .analyze(
            ExampleDomain(),
            _catalog(
                ExampleSolver(
                    name="exploding",
                    fail=True,
                )
            ),
        )
        .strategies[0]
        .execute()
    )
    assert isinstance(exploding.state, Failed)
    assert exploding.failed
    assert not exploding.succeeded
    assert exploding.failure == Failure(
        error_type="RuntimeError",
        message="exploding failed",
    )
    assert exploding.to_dict()["failure"]["error_type"] == "RuntimeError"

    partial = (
        Analyzer()
        .analyze(
            ExampleDomain(),
            _catalog(
                ExampleSolver(
                    name="partial",
                    status="partial",
                )
            ),
        )
        .strategies[0]
        .execute()
    )
    assert partial.failed
    assert partial.failure is not None
    assert "non-complete" in partial.failure.message


def test_execution_state_objects_are_polymorphic() -> None:
    assert Pending().code == "pending"
    assert not Pending().succeeded
    assert not Pending().failed
    assert Complete().succeeded
    assert not Complete().failed
    assert Failed().failed
    assert not Failed().succeeded
    assert Failure(
        error_type="ValueError",
        message="bad",
    ).to_dict() == {
        "error_type": "ValueError",
        "message": "bad",
    }
