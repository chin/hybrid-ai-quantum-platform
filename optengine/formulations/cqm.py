from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from typing import Any, ClassVar, Mapping

from optengine.errors import MissingDependencyError
from optengine.formulations.base import Formulation, Model as BaseModel
from optengine.mathematics import (
    Constraint,
    Curve,
    Expression,
    ValueType,
    Variable,
)
from optengine.objective import Objective


def _require_dimod() -> Any:
    try:
        import dimod
    except ImportError as error:
        raise MissingDependencyError("dimod", "CQM") from error
    return dimod


def _variable(dimod: Any, variable: Variable) -> Any:
    if variable.value_type is ValueType.BINARY:
        return dimod.Binary(variable.identifier)
    if variable.value_type is ValueType.INTEGER:
        lower = 0 if variable.lower_bound is None else variable.lower_bound
        upper = 2**31 - 1 if variable.upper_bound is None else variable.upper_bound
        return dimod.Integer(
            variable.identifier,
            lower_bound=lower,
            upper_bound=upper,
        )
    if variable.value_type is ValueType.REAL:
        lower = -1e30 if variable.lower_bound is None else variable.lower_bound
        upper = 1e30 if variable.upper_bound is None else variable.upper_bound
        return dimod.Real(
            variable.identifier,
            lower_bound=lower,
            upper_bound=upper,
        )
    raise TypeError(f"CQM cannot express {variable.value_type.value} variables.")


def _polynomial(
    expression: Expression | Constraint,
    symbols: Mapping[Any, Any],
) -> Any:
    value: Any = float(expression.constant)
    for term in expression.linear_terms:
        value += float(term.coefficient) * symbols[term.variable.identifier]
    for term in expression.quadratic_terms:
        value += (
            float(term.coefficient)
            * symbols[term.first.identifier]
            * symbols[term.second.identifier]
        )
    return value


class CQM(Formulation):
    name: ClassVar[str] = "cqm"

    capability = Formulation.Capability(
        input_types=frozenset(
            {
                ValueType.BINARY,
                ValueType.INTEGER,
                ValueType.REAL,
            }
        ),
        maximum_degree=2,
        supports_constraints=True,
        maximum_constraint_degree=2,
        maximum_outputs=1,
    )

    @property
    def available(self) -> bool:
        return importlib.util.find_spec("dimod") is not None

    @dataclass(frozen=True, kw_only=True)
    class Model(BaseModel):
        payload: Any

    def _express(self, objective: Objective) -> BaseModel:
        dimod = _require_dimod()
        expression = objective.expression
        cqm = dimod.ConstrainedQuadraticModel()
        symbols = {
            variable.identifier: _variable(dimod, variable)
            for variable in expression.variables
        }

        objective_value = _polynomial(expression, symbols)
        if objective.sense == "maximize":
            objective_value = -objective_value
        cqm.set_objective(objective_value)

        for constraint in expression.constraints:
            left = _polynomial(constraint, symbols)
            if constraint.relation == "eq":
                comparison = left == float(constraint.bound)
            elif constraint.relation == "le":
                comparison = left <= float(constraint.bound)
            else:
                comparison = left >= float(constraint.bound)
            cqm.add_constraint(
                comparison,
                label=constraint.name,
            )

        return self.Model(
            formulation=self,
            objective=objective,
            payload=cqm,
            curve=objective.curve,
            metadata={
                "objective_sense": objective.sense,
                "source_curve": dict(objective.curve.canonical),
            },
        )


# Transitional public alias. New code should use CQM.
CQMFormulation = CQM
