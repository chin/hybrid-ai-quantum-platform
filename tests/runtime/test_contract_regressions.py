from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Mapping

import pytest

from optengine.catalog import Catalog
from optengine.compatibility import Compatibility
from optengine.formulations.base import Formulation, Model
from optengine.mathematics import Curve, ValueType
from optengine.operations.base import Operation
from optengine.solvers.base import Solver
from tests.support import (
    ExampleDomain,
    ExampleFormulation,
    ExampleOperation,
    ExampleSolver,
)


def test_compatibility_value_object() -> None:
    accepted = Compatibility.accepted(evidence={"x": 1})
    rejected = Compatibility.rejected("", evidence={"y": 2})
    explicit = Compatibility.rejected("first", "second")

    assert accepted
    assert accepted.to_dict() == {
        "supported": True,
        "reasons": [],
        "evidence": {"x": 1},
    }
    assert not rejected
    assert rejected.reasons == ("unsupported",)
    assert explicit.reasons == ("first", "second")


def test_formulation_capability_exhaustive_rejection_reasons() -> None:
    capability = Formulation.Capability(
        input_types=frozenset({ValueType.BINARY}),
        output_types=frozenset({ValueType.INTEGER}),
        maximum_degree=1,
        supports_constraints=False,
        maximum_constraint_degree=0,
        maximum_inputs=1,
        maximum_outputs=0,
    )
    curve = Curve(
        input_types=(ValueType.REAL, ValueType.REAL),
        input_count=2,
        output_types=(ValueType.REAL,),
        output_count=1,
        degree=2,
        constraint_count=1,
        constraint_degrees=(2,),
    )
    result = capability.evaluate(curve)
    assert not result
    assert set(result.reasons) == {
        "unsupported input value type",
        "unsupported output value type",
        "objective degree exceeds capability",
        "constraints are not supported",
        "constraint degree exceeds capability",
        "input count exceeds capability",
        "output count exceeds capability",
    }
    assert not capability.supports(curve)


def test_formulation_expression_contract_and_availability() -> None:
    domain = ExampleDomain()
    formulation = ExampleFormulation(tag="x")
    model = formulation.express(domain.objective)

    assert isinstance(model, Model)
    assert model.formulation is formulation
    assert model.objective.canonical == domain.objective.canonical
    assert model.curve == domain.objective.curve
    assert model.metadata["tag"] == "x"
    assert formulation.signature == {
        "name": "example-formulation",
        "configuration": {"tag": "x"},
    }

    @dataclass(frozen=True, kw_only=True)
    class Unavailable(ExampleFormulation):
        name: ClassVar[str] = "unavailable"

        @property
        def available(self) -> bool:
            return False

    unavailable = Unavailable()
    compatibility = unavailable.compatibility(domain.objective)
    assert not compatibility
    assert compatibility.reasons == ("Formulation is unavailable",)
    assert unavailable.express(domain.objective) is None


def test_model_local_behavior_filters_operations_and_decodes() -> None:
    domain = ExampleDomain()
    model = ExampleFormulation().express(domain.objective)
    assert model is not None

    accepted = ExampleOperation(limit=2)
    rejected = ExampleOperation(limit=1)
    assert model.operations((rejected, accepted)) == (accepted,)
    assert model.compatibility(rejected).supported is False
    assert model.to_dict()["fingerprint"] == model.fingerprint

    solver = ExampleSolver()
    strategy = _strategy(
        domain=domain,
        model=model,
        operation=accepted,
        solver=solver,
    )
    result = solver.execute(accepted.prepare(model))
    candidate = model.decode(result, strategy)
    assert candidate.values == {"x": 1, "y": 1}
    assert candidate.strategy == strategy.name


def test_operation_capability_prepare_and_solver_filtering() -> None:
    domain = ExampleDomain()
    model = ExampleFormulation().express(domain.objective)
    assert model is not None

    operation = ExampleOperation(limit=2)
    request = operation.prepare(model)
    assert request.model is model
    assert request.operation is operation
    assert request.budget == {"attempts": 1}
    assert request.to_dict()["operation"] == "example-operation"
    assert operation.signature["configuration"]["limit"] == 2

    with pytest.raises(TypeError, match="cannot prepare"):
        ExampleOperation(limit=1).prepare(model)

    accepted = ExampleSolver(name="accepted")
    unavailable = ExampleSolver(
        name="unavailable",
        available_flag=False,
    )
    assert operation.solvers(
        model,
        (unavailable, accepted),
    ) == (accepted,)


def test_operation_capability_all_rejection_paths() -> None:
    domain = ExampleDomain()
    model = ExampleFormulation().express(domain.objective)
    assert model is not None

    class OtherModel(Model):
        pass

    capability = Operation.Capability(
        input_types=frozenset({ValueType.REAL}),
        maximum_degree=0,
        supports_constraints=False,
        maximum_inputs=1,
        model_types=(OtherModel,),
    )
    result = capability.evaluate(model)
    assert not result
    assert set(result.reasons) == {
        "unsupported Model type",
        "unsupported Model input value type",
        "Model degree exceeds capability",
        "Model input count exceeds capability",
    }
    assert not capability.supports(model)


def test_solver_capability_all_rejection_paths_and_result() -> None:
    domain = ExampleDomain()
    model = ExampleFormulation().express(domain.objective)
    assert model is not None
    operation = ExampleOperation(limit=2)

    @dataclass(frozen=True, kw_only=True)
    class OtherOperation(ExampleOperation):
        name: ClassVar[str] = "other-operation"

    class OtherModel(Model):
        pass

    capability = Solver.Capability(
        operation_types=(OtherOperation,),
        model_types=(OtherModel,),
        input_types=frozenset({ValueType.REAL}),
        maximum_inputs=1,
        supports_constraints=False,
    )
    solver = ExampleSolver(
        name="unavailable",
        available_flag=False,
    )
    result = capability.evaluate(
        solver=solver,
        operation=operation,
        model=model,
    )
    assert not result
    assert set(result.reasons) == {
        "Solver is unavailable",
        "unsupported Operation type",
        "unsupported Model type",
        "unsupported Model input value type",
        "Model input count exceeds Solver capability",
    }
    assert not capability.supports(
        solver=solver,
        operation=operation,
        model=model,
    )

    result_object = Solver.Result(
        values={"x": 1},
        native_score=-1.0,
        status="complete",
        runtime_s=0.1,
        resource_cost=2.0,
        metrics={"m": 1},
        metadata={"n": 2},
        provenance={"p": 3},
    )
    assert result_object.complete
    assert result_object.to_dict()["provenance"] == {"p": 3}
    assert not Solver.Result(
        values={},
        native_score=None,
        status="partial",
    ).complete


def test_catalog_canonicalization_and_duplicate_rejection() -> None:
    catalog = Catalog(
        formulations=(ExampleFormulation(),),
        operations=(ExampleOperation(),),
        solvers=(ExampleSolver(),),
    )
    assert catalog.formulation_names == ("example-formulation",)
    assert catalog.operation_names == ("example-operation",)
    assert catalog.solver_names == ("example-solver",)
    assert catalog.fingerprint
    assert catalog.canonical["formulations"][0]["name"] == ("example-formulation")

    with pytest.raises(ValueError, match="Formulation"):
        Catalog(
            formulations=(
                ExampleFormulation(tag="a"),
                ExampleFormulation(tag="b"),
            ),
            operations=(),
            solvers=(),
        )
    with pytest.raises(ValueError, match="Operation"):
        Catalog(
            formulations=(),
            operations=(ExampleOperation(), ExampleOperation()),
            solvers=(),
        )
    with pytest.raises(ValueError, match="Solver"):
        Catalog(
            formulations=(),
            operations=(),
            solvers=(
                ExampleSolver(name="same"),
                ExampleSolver(name="same"),
            ),
        )


def _strategy(
    *,
    domain: ExampleDomain,
    model: Model,
    operation: Operation,
    solver: Solver,
):
    from optengine.strategy import Strategy

    return Strategy(
        domain=domain,
        formulation=model.formulation,
        model=model,
        operation=operation,
        solver=solver,
    )
