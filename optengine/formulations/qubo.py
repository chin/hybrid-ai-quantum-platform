from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from math import isfinite
from typing import Any, ClassVar, Mapping

from optengine.errors import MissingDependencyError
from optengine.formulations.base import Formulation, Model as BaseModel
from optengine.mathematics import Curve, ValueType
from optengine.objective import Objective


def _require_dimod() -> Any:
    try:
        import dimod
    except ImportError as error:
        raise MissingDependencyError("dimod", "QUBO") from error
    return dimod


def _ordered_pair(first: Any, second: Any) -> tuple[Any, Any]:
    if repr(first) <= repr(second):
        return first, second
    return second, first


@dataclass(frozen=True, kw_only=True)
class QUBO(Formulation):
    name: ClassVar[str] = "qubo"

    capability = Formulation.Capability(
        input_types=frozenset({ValueType.BINARY}),
        maximum_degree=2,
        supports_constraints=True,
        maximum_constraint_degree=2,
        maximum_outputs=1,
    )

    lagrange_multiplier: float | None = None

    def __post_init__(self) -> None:
        if self.lagrange_multiplier is not None and (
            not isfinite(float(self.lagrange_multiplier))
            or self.lagrange_multiplier <= 0.0
        ):
            raise ValueError("lagrange_multiplier must be a finite positive value.")

    @property
    def available(self) -> bool:
        return importlib.util.find_spec("dimod") is not None

    @property
    def configuration(self) -> Mapping[str, Any]:
        return {
            "lagrange_multiplier": self.lagrange_multiplier,
        }

    @dataclass(frozen=True, kw_only=True)
    class Model(BaseModel):
        payload: Any
        coefficients: Mapping[tuple[Any, Any], float]

        def to_dict(self) -> Mapping[str, Any]:
            payload = dict(super().to_dict())
            payload["coefficient_count"] = len(self.coefficients)
            return payload

    def _express(self, objective: Objective) -> BaseModel:
        dimod = _require_dimod()
        expression = objective.expression

        if expression.constraints:
            from optengine.formulations.cqm import CQM

            source_model = CQM().express(objective)
            if source_model is None:
                raise TypeError("QUBO could not construct a CQM source model.")
            bqm, inverter = dimod.cqm_to_bqm(
                source_model.payload,
                lagrange_multiplier=self.lagrange_multiplier,
            )
            sample_decoder = lambda values: dict(inverter(values))
            source = "cqm"
        else:
            multiplier = -1.0 if objective.sense == "maximize" else 1.0
            coefficients: dict[tuple[Any, Any], float] = {}

            for term in expression.linear_terms:
                key = (
                    term.variable.identifier,
                    term.variable.identifier,
                )
                coefficients[key] = coefficients.get(key, 0.0) + (
                    multiplier * float(term.coefficient)
                )

            for term in expression.quadratic_terms:
                key = _ordered_pair(
                    term.first.identifier,
                    term.second.identifier,
                )
                coefficients[key] = coefficients.get(key, 0.0) + (
                    multiplier * float(term.coefficient)
                )

            bqm = dimod.BinaryQuadraticModel.from_qubo(
                coefficients,
                offset=multiplier * float(expression.constant),
            )
            sample_decoder = None
            source = "expression"

        coefficients = {
            (variable, variable): float(bias) for variable, bias in bqm.linear.items()
        }
        for (first, second), bias in bqm.quadratic.items():
            key = _ordered_pair(first, second)
            coefficients[key] = coefficients.get(key, 0.0) + float(bias)

        model_curve = Curve(
            input_types=tuple(ValueType.BINARY for _ in bqm.variables),
            input_count=bqm.num_variables,
            output_types=(ValueType.REAL,),
            output_count=1,
            degree=2 if bqm.quadratic else (1 if bqm.linear else 0),
            constraint_count=0,
            constraint_degrees=(),
        )

        return self.Model(
            formulation=self,
            objective=objective,
            payload=bqm,
            curve=model_curve,
            sample_decoder=sample_decoder,
            coefficients=coefficients,
            metadata={
                "objective_sense": objective.sense,
                "source": source,
                "source_curve": dict(objective.curve.canonical),
                "lagrange_multiplier": self.lagrange_multiplier,
            },
        )


# Transitional public aliases. New code should use QUBO.
QUBOFormulation = QUBO
QUBOModel = QUBO.Model
