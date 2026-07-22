from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Any, Hashable, Literal, Mapping

from optengine.identity import fingerprint, identifier_value


Number = int | float
ObjectiveSense = Literal["minimize", "maximize"]
ConstraintRelation = Literal["eq", "le", "ge"]


class ValueType(str, Enum):
    BINARY = "binary"
    INTEGER = "integer"
    REAL = "real"
    CATEGORICAL = "categorical"


@dataclass(frozen=True, kw_only=True)
class Variable:
    identifier: Hashable
    value_type: ValueType
    lower_bound: Number | None = None
    upper_bound: Number | None = None

    def __post_init__(self) -> None:
        if self.lower_bound is not None and not isfinite(float(self.lower_bound)):
            raise ValueError("Variable lower_bound must be finite.")
        if self.upper_bound is not None and not isfinite(float(self.upper_bound)):
            raise ValueError("Variable upper_bound must be finite.")
        if (
            self.lower_bound is not None
            and self.upper_bound is not None
            and self.lower_bound > self.upper_bound
        ):
            raise ValueError("Variable lower_bound cannot exceed upper_bound.")
        if self.value_type is ValueType.BINARY:
            if self.lower_bound not in (None, 0, 0.0):
                raise ValueError(
                    "Binary variables cannot have a lower bound other than 0."
                )
            if self.upper_bound not in (None, 1, 1.0):
                raise ValueError(
                    "Binary variables cannot have an upper bound other than 1."
                )

    @property
    def canonical(self) -> Mapping[str, Any]:
        return {
            "identifier": identifier_value(self.identifier),
            "value_type": self.value_type.value,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
        }


@dataclass(frozen=True, kw_only=True)
class LinearTerm:
    variable: Variable
    coefficient: float

    def __post_init__(self) -> None:
        if not isfinite(float(self.coefficient)):
            raise ValueError("Linear coefficient must be finite.")

    @property
    def canonical(self) -> Mapping[str, Any]:
        return {
            "variable": self.variable.canonical,
            "coefficient": float(self.coefficient),
        }


@dataclass(frozen=True, kw_only=True)
class QuadraticTerm:
    first: Variable
    second: Variable
    coefficient: float

    def __post_init__(self) -> None:
        if not isfinite(float(self.coefficient)):
            raise ValueError("Quadratic coefficient must be finite.")

    @property
    def canonical(self) -> Mapping[str, Any]:
        ordered = sorted(
            (self.first.canonical, self.second.canonical),
            key=lambda value: repr(value),
        )
        return {
            "first": ordered[0],
            "second": ordered[1],
            "coefficient": float(self.coefficient),
        }


@dataclass(frozen=True, kw_only=True)
class Constraint:
    name: str
    relation: ConstraintRelation
    bound: float
    linear_terms: tuple[LinearTerm, ...] = ()
    quadratic_terms: tuple[QuadraticTerm, ...] = ()
    constant: float = 0.0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Constraint name cannot be empty.")
        if not isfinite(float(self.bound)):
            raise ValueError("Constraint bound must be finite.")
        if not isfinite(float(self.constant)):
            raise ValueError("Constraint constant must be finite.")

    @property
    def degree(self) -> int:
        if self.quadratic_terms:
            return 2
        if self.linear_terms:
            return 1
        return 0

    def evaluate(self, values: Mapping[Hashable, Number]) -> float:
        total = float(self.constant)
        total += sum(
            float(term.coefficient) * float(values[term.variable.identifier])
            for term in self.linear_terms
        )
        total += sum(
            float(term.coefficient)
            * float(values[term.first.identifier])
            * float(values[term.second.identifier])
            for term in self.quadratic_terms
        )
        return total

    def satisfied(
        self,
        values: Mapping[Hashable, Number],
        *,
        tolerance: float = 1e-9,
    ) -> bool:
        value = self.evaluate(values)
        if self.relation == "eq":
            return abs(value - self.bound) <= tolerance
        if self.relation == "le":
            return value <= self.bound + tolerance
        return value >= self.bound - tolerance

    @property
    def canonical(self) -> Mapping[str, Any]:
        return {
            "name": self.name,
            "relation": self.relation,
            "bound": float(self.bound),
            "linear_terms": tuple(
                term.canonical
                for term in sorted(
                    self.linear_terms,
                    key=lambda term: repr(term.variable.identifier),
                )
            ),
            "quadratic_terms": tuple(
                term.canonical
                for term in sorted(
                    self.quadratic_terms,
                    key=lambda term: (
                        repr(term.first.identifier),
                        repr(term.second.identifier),
                    ),
                )
            ),
            "constant": float(self.constant),
        }


@dataclass(frozen=True, kw_only=True)
class Curve:
    """Structural mathematical profile used for real-time compatibility."""

    input_types: tuple[ValueType, ...]
    input_count: int
    output_types: tuple[ValueType, ...]
    output_count: int
    degree: int
    constraint_count: int
    constraint_degrees: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.input_count < 0 or self.output_count < 0:
            raise ValueError("Curve value counts cannot be negative.")
        if self.input_count != len(self.input_types):
            raise ValueError("Curve input_count must match input_types.")
        if self.output_count != len(self.output_types):
            raise ValueError("Curve output_count must match output_types.")
        if self.degree < 0:
            raise ValueError("Curve degree cannot be negative.")
        if self.constraint_count != len(self.constraint_degrees):
            raise ValueError("Curve constraint_count must match constraint_degrees.")
        if any(degree < 0 for degree in self.constraint_degrees):
            raise ValueError("Curve constraint degrees cannot be negative.")

    @property
    def distinct_input_types(self) -> frozenset[ValueType]:
        return frozenset(self.input_types)

    @property
    def distinct_output_types(self) -> frozenset[ValueType]:
        return frozenset(self.output_types)

    @property
    def constrained(self) -> bool:
        return self.constraint_count > 0

    def count(self, value_type: ValueType) -> int:
        return self.input_types.count(value_type)

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.canonical)

    @property
    def canonical(self) -> Mapping[str, Any]:
        return {
            "input_types": tuple(value.value for value in self.input_types),
            "input_count": self.input_count,
            "output_types": tuple(value.value for value in self.output_types),
            "output_count": self.output_count,
            "degree": self.degree,
            "constraint_count": self.constraint_count,
            "constraint_degrees": self.constraint_degrees,
        }


@dataclass(frozen=True, kw_only=True)
class Expression:
    variables: tuple[Variable, ...]
    linear_terms: tuple[LinearTerm, ...] = ()
    quadratic_terms: tuple[QuadraticTerm, ...] = ()
    constraints: tuple[Constraint, ...] = ()
    constant: float = 0.0

    def __post_init__(self) -> None:
        if not isfinite(float(self.constant)):
            raise ValueError("Expression constant must be finite.")

        identifiers = tuple(variable.identifier for variable in self.variables)
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("Expression variable identifiers must be unique.")

        declared = set(identifiers)
        referenced = {term.variable.identifier for term in self.linear_terms}
        referenced.update(
            identifier
            for term in self.quadratic_terms
            for identifier in (term.first.identifier, term.second.identifier)
        )
        referenced.update(
            term.variable.identifier
            for constraint in self.constraints
            for term in constraint.linear_terms
        )
        referenced.update(
            identifier
            for constraint in self.constraints
            for term in constraint.quadratic_terms
            for identifier in (term.first.identifier, term.second.identifier)
        )
        unknown = referenced - declared
        if unknown:
            raise ValueError(
                "Expression terms reference undeclared variables: "
                f"{sorted((repr(value) for value in unknown))}"
            )

        names = tuple(constraint.name for constraint in self.constraints)
        if len(set(names)) != len(names):
            raise ValueError("Expression constraint names must be unique.")

    @property
    def degree(self) -> int:
        if self.quadratic_terms:
            return 2
        if self.linear_terms:
            return 1
        return 0

    @property
    def curve(self) -> Curve:
        return Curve(
            input_types=tuple(variable.value_type for variable in self.variables),
            input_count=len(self.variables),
            output_types=(ValueType.REAL,),
            output_count=1,
            degree=self.degree,
            constraint_count=len(self.constraints),
            constraint_degrees=tuple(
                constraint.degree for constraint in self.constraints
            ),
        )

    def evaluate(self, values: Mapping[Hashable, Number]) -> float:
        total = float(self.constant)
        total += sum(
            float(term.coefficient) * float(values[term.variable.identifier])
            for term in self.linear_terms
        )
        total += sum(
            float(term.coefficient)
            * float(values[term.first.identifier])
            * float(values[term.second.identifier])
            for term in self.quadratic_terms
        )
        return total

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.canonical)

    @property
    def canonical(self) -> Mapping[str, Any]:
        return {
            "variables": tuple(
                variable.canonical
                for variable in sorted(
                    self.variables,
                    key=lambda variable: repr(variable.identifier),
                )
            ),
            "linear_terms": tuple(
                term.canonical
                for term in sorted(
                    self.linear_terms,
                    key=lambda term: repr(term.variable.identifier),
                )
            ),
            "quadratic_terms": tuple(
                term.canonical
                for term in sorted(
                    self.quadratic_terms,
                    key=lambda term: (
                        repr(term.first.identifier),
                        repr(term.second.identifier),
                    ),
                )
            ),
            "constraints": tuple(
                constraint.canonical
                for constraint in sorted(
                    self.constraints,
                    key=lambda constraint: constraint.name,
                )
            ),
            "constant": float(self.constant),
        }
