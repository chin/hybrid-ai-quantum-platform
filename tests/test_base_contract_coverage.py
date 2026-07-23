from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import pytest

from optengine.analysis import Analyzer
from optengine.catalog import Catalog
from optengine.engine import OptEngine
from optengine.evaluation import Evaluation, Feasible, Infeasible
from optengine.formulations.base import Formulation, Model
from optengine.mathematics import Curve, ValueType
from optengine.operations.base import Operation
from optengine.recommendation import Recommendation
from optengine.solvers.base import Solver
from optengine.stages.decide import decide
from optengine.stages.evaluate import evaluate
from optengine.stages.explain import explain
from optengine.stages.write import write
from optengine.utility.operational import OperationalUtility
from tests.support import (
    ExampleDomain,
    ExampleFormulation,
    ExampleOperation,
    ExampleSolver,
)


class DefaultEvaluation(Evaluation):
    @property
    def feasible(self) -> bool:
        return True

    @property
    def quality(self) -> float:
        return 1.0

    @property
    def metrics(self) -> Mapping[str, Any]:
        return {}

    @property
    def policy_evidence(self) -> Mapping[str, Any]:
        return {"policy": 1}

    def to_dict(self) -> Mapping[str, Any]:
        return {}


class MinimalFormulation(Formulation):
    name = "minimal-formulation"
    capability = Formulation.Capability(
        input_types=frozenset({ValueType.BINARY}),
    )

    def _express(self, objective):
        return Model(
            formulation=self,
            objective=objective,
            payload=None,
            curve=objective.curve,
        )


class MinimalOperation(Operation):
    name = "minimal-operation"

    @property
    def capability(self) -> Operation.Capability:
        return Operation.Capability(
            input_types=frozenset({ValueType.BINARY}),
        )


class MinimalSolver(Solver):
    name = "minimal-solver"
    capability = Solver.Capability(
        operation_types=(MinimalOperation,),
        model_types=(Model,),
        input_types=frozenset({ValueType.BINARY}),
    )

    def execute(self, request):
        return Solver.Result(
            values={"x": 0, "y": 0},
            native_score=0.0,
            status="complete",
        )


def test_default_base_properties_and_state_messages() -> None:
    evaluation = DefaultEvaluation()
    assert evaluation.utility_inputs == {}
    assert evaluation.policy_evidence == {"policy": 1}
    assert evaluation.evidence_for_utility() == {"policy": 1}
    assert Feasible().message == "feasible"
    assert Infeasible().message == "infeasible"

    formulation = MinimalFormulation()
    operation = MinimalOperation()
    solver = MinimalSolver()
    assert formulation.available
    assert formulation.configuration == {}
    assert operation.configuration == {}
    assert operation.budget == {}
    assert solver.available
    assert not solver.reference
    assert solver.configuration == {}


def test_objective_and_model_fingerprints_and_sample_decoder() -> None:
    domain = ExampleDomain()
    assert domain.objective.fingerprint == domain.objective.fingerprint

    formulation = MinimalFormulation()
    model = Model(
        formulation=formulation,
        objective=domain.objective,
        payload=None,
        curve=domain.objective.curve,
        sample_decoder=lambda values: {
            "x": values["x"],
            "y": 1,
        },
    )
    operation = MinimalOperation()
    solver = MinimalSolver()
    from optengine.strategy import Strategy

    strategy = Strategy(
        domain=domain,
        formulation=formulation,
        model=model,
        operation=operation,
        solver=solver,
    )
    result = Solver.Result(
        values={"x": 1, "y": 0},
        native_score=0.0,
        status="complete",
    )
    assert model.decode(result, strategy).values == {
        "x": 1,
        "y": 1,
    }


def test_constraint_rejection_in_operation_and_solver_capabilities() -> None:
    domain = ExampleDomain()
    formulation = MinimalFormulation()
    constrained_curve = Curve(
        input_types=(ValueType.BINARY, ValueType.BINARY),
        input_count=2,
        output_types=(ValueType.REAL,),
        output_count=1,
        degree=1,
        constraint_count=1,
        constraint_degrees=(1,),
    )
    model = Model(
        formulation=formulation,
        objective=domain.objective,
        payload=None,
        curve=constrained_curve,
    )
    operation = MinimalOperation()
    operation_result = operation.compatibility(model)
    assert not operation_result
    assert "constrained Models are not supported" in (operation_result.reasons)

    solver_result = MinimalSolver().compatibility(
        operation=operation,
        model=model,
    )
    assert not solver_result
    assert "constrained Models are not supported" in (solver_result.reasons)


def test_analyzer_records_solver_rejection_and_deduplicates_fingerprints() -> None:
    domain = ExampleDomain()
    unavailable = ExampleSolver(
        name="unavailable",
        available_flag=False,
    )
    available = ExampleSolver(name="available")
    analysis = Analyzer().analyze(
        domain,
        Catalog(
            formulations=(ExampleFormulation(),),
            operations=(ExampleOperation(limit=2),),
            solvers=(unavailable, available),
        ),
    )
    assert analysis.strategy_names == (
        "example:example-formulation:example-operation:available",
    )
    assert any(
        record.stage == "solver" and not record.supported
        for record in analysis.compatibility
    )

    @dataclass(frozen=True, kw_only=True)
    class SameSignatureSolver(ExampleSolver):
        @property
        def signature(self) -> Mapping[str, Any]:
            return {"name": "same", "configuration": {}}

    deduplicated = Analyzer().analyze(
        domain,
        Catalog(
            formulations=(ExampleFormulation(),),
            operations=(ExampleOperation(limit=2),),
            solvers=(
                SameSignatureSolver(name="one"),
                SameSignatureSolver(name="two"),
            ),
        ),
    )
    assert len(deduplicated.strategies) == 1


def test_stage_preconditions_fail_at_the_correct_boundary(tmp_path) -> None:
    class Null:
        pass

    engine = OptEngine(
        domain=ExampleDomain(),
        catalog=Catalog(
            formulations=(ExampleFormulation(),),
            operations=(ExampleOperation(limit=2),),
            solvers=(ExampleSolver(),),
        ),
        analyzer=Analyzer(),
        utility=OperationalUtility(),
        policy=Null(),
        explainer=Null(),
        writer=Null(),
        recommendation=Recommendation(run_id="test"),
        output_dir=tmp_path,
    )
    with pytest.raises(RuntimeError, match="not been analyzed"):
        evaluate(engine)
    with pytest.raises(RuntimeError, match="no analysis"):
        decide(engine)
    with pytest.raises(RuntimeError, match="requires analysis"):
        explain(engine)
    with pytest.raises(RuntimeError, match="requires an explanation"):
        write(engine)
