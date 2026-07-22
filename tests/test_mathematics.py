from __future__ import annotations

from math import inf, nan

import pytest

from optengine.identity import canonical_value, fingerprint, identifier_value
from optengine.mathematics import (
    Constraint,
    Curve,
    Expression,
    LinearTerm,
    QuadraticTerm,
    ValueType,
    Variable,
)


def test_variable_validation_and_canonical_identity() -> None:
    variable = Variable(
        identifier=("x", 1),
        value_type=ValueType.INTEGER,
        lower_bound=-2,
        upper_bound=4,
    )
    assert variable.canonical["value_type"] == "integer"
    assert variable.canonical["identifier"] == identifier_value(("x", 1))

    with pytest.raises(ValueError, match="lower_bound"):
        Variable(
            identifier="x",
            value_type=ValueType.REAL,
            lower_bound=inf,
        )
    with pytest.raises(ValueError, match="upper_bound"):
        Variable(
            identifier="x",
            value_type=ValueType.REAL,
            upper_bound=nan,
        )
    with pytest.raises(ValueError, match="cannot exceed"):
        Variable(
            identifier="x",
            value_type=ValueType.INTEGER,
            lower_bound=2,
            upper_bound=1,
        )
    with pytest.raises(ValueError, match="lower bound"):
        Variable(
            identifier="x",
            value_type=ValueType.BINARY,
            lower_bound=-1,
        )
    with pytest.raises(ValueError, match="upper bound"):
        Variable(
            identifier="x",
            value_type=ValueType.BINARY,
            upper_bound=2,
        )


def test_terms_reject_nonfinite_coefficients_and_canonicalize() -> None:
    x = Variable(identifier="x", value_type=ValueType.BINARY)
    y = Variable(identifier="y", value_type=ValueType.BINARY)

    linear = LinearTerm(variable=x, coefficient=2.0)
    quadratic = QuadraticTerm(
        first=y,
        second=x,
        coefficient=-3.0,
    )
    assert linear.canonical["coefficient"] == 2.0
    assert quadratic.canonical["coefficient"] == -3.0
    assert (
        quadratic.canonical
        == QuadraticTerm(
            first=x,
            second=y,
            coefficient=-3.0,
        ).canonical
    )

    with pytest.raises(ValueError, match="Linear"):
        LinearTerm(variable=x, coefficient=inf)
    with pytest.raises(ValueError, match="Quadratic"):
        QuadraticTerm(first=x, second=y, coefficient=nan)


@pytest.mark.parametrize(
    ("relation", "value", "expected"),
    [
        ("eq", 2.0, True),
        ("eq", 2.01, False),
        ("le", 1.5, True),
        ("le", 2.5, False),
        ("ge", 2.5, True),
        ("ge", 1.5, False),
    ],
)
def test_constraint_evaluation_and_satisfaction(
    relation: str,
    value: float,
    expected: bool,
) -> None:
    x = Variable(identifier="x", value_type=ValueType.REAL)
    constraint = Constraint(
        name=f"constraint-{relation}",
        relation=relation,
        bound=2.0,
        linear_terms=(LinearTerm(variable=x, coefficient=1.0),),
    )
    assert constraint.degree == 1
    assert constraint.evaluate({"x": value}) == value
    assert constraint.satisfied({"x": value}) is expected
    assert constraint.canonical["relation"] == relation


def test_constraint_quadratic_constant_and_validation() -> None:
    x = Variable(identifier="x", value_type=ValueType.REAL)
    constraint = Constraint(
        name="quadratic",
        relation="eq",
        bound=5.0,
        quadratic_terms=(QuadraticTerm(first=x, second=x, coefficient=1.0),),
        constant=1.0,
    )
    assert constraint.degree == 2
    assert constraint.evaluate({"x": 2.0}) == 5.0

    constant = Constraint(
        name="constant",
        relation="ge",
        bound=1.0,
        constant=1.0,
    )
    assert constant.degree == 0
    assert constant.satisfied({})

    with pytest.raises(ValueError, match="name"):
        Constraint(name=" ", relation="eq", bound=0.0)
    with pytest.raises(ValueError, match="bound"):
        Constraint(name="x", relation="eq", bound=inf)
    with pytest.raises(ValueError, match="constant"):
        Constraint(name="x", relation="eq", bound=0.0, constant=nan)


def test_curve_properties_validation_and_fingerprint() -> None:
    curve = Curve(
        input_types=(ValueType.BINARY, ValueType.INTEGER),
        input_count=2,
        output_types=(ValueType.REAL,),
        output_count=1,
        degree=2,
        constraint_count=1,
        constraint_degrees=(1,),
    )
    assert curve.distinct_input_types == {
        ValueType.BINARY,
        ValueType.INTEGER,
    }
    assert curve.distinct_output_types == {ValueType.REAL}
    assert curve.constrained
    assert curve.count(ValueType.BINARY) == 1
    assert curve.fingerprint == fingerprint(curve.canonical)

    invalid = [
        dict(input_count=-1),
        dict(output_count=-1),
        dict(input_count=3),
        dict(output_count=2),
        dict(degree=-1),
        dict(constraint_count=2),
        dict(constraint_degrees=(-1,)),
    ]
    base = {
        "input_types": (ValueType.BINARY, ValueType.INTEGER),
        "input_count": 2,
        "output_types": (ValueType.REAL,),
        "output_count": 1,
        "degree": 2,
        "constraint_count": 1,
        "constraint_degrees": (1,),
    }
    for update in invalid:
        with pytest.raises(ValueError):
            Curve(**{**base, **update})


def test_expression_build_evaluate_curve_canonical_and_validation() -> None:
    x = Variable(identifier="x", value_type=ValueType.BINARY)
    y = Variable(identifier="y", value_type=ValueType.BINARY)
    constraint = Constraint(
        name="sum",
        relation="eq",
        bound=1.0,
        linear_terms=(
            LinearTerm(variable=x, coefficient=1.0),
            LinearTerm(variable=y, coefficient=1.0),
        ),
    )
    expression = Expression(
        variables=(y, x),
        linear_terms=(LinearTerm(variable=x, coefficient=2.0),),
        quadratic_terms=(QuadraticTerm(first=x, second=y, coefficient=3.0),),
        constraints=(constraint,),
        constant=1.0,
    )
    assert expression.degree == 2
    assert expression.evaluate({"x": 1, "y": 1}) == 6.0
    assert expression.curve.degree == 2
    assert expression.curve.constraint_count == 1
    assert expression.fingerprint == fingerprint(expression.canonical)
    assert expression.canonical["variables"][0]["identifier"]["repr"] == "'x'"

    linear = Expression(
        variables=(x,),
        linear_terms=(LinearTerm(variable=x, coefficient=1.0),),
    )
    assert linear.degree == 1
    assert Expression(variables=(x,)).degree == 0

    with pytest.raises(ValueError, match="constant"):
        Expression(variables=(), constant=inf)
    with pytest.raises(ValueError, match="unique"):
        Expression(variables=(x, x))
    with pytest.raises(ValueError, match="undeclared"):
        Expression(
            variables=(x,),
            linear_terms=(LinearTerm(variable=y, coefficient=1.0),),
        )
    with pytest.raises(ValueError, match="undeclared"):
        Expression(
            variables=(x,),
            quadratic_terms=(QuadraticTerm(first=x, second=y, coefficient=1.0),),
        )
    with pytest.raises(ValueError, match="undeclared"):
        Expression(
            variables=(x,),
            constraints=(
                Constraint(
                    name="unknown",
                    relation="eq",
                    bound=0,
                    linear_terms=(LinearTerm(variable=y, coefficient=1.0),),
                ),
            ),
        )
    with pytest.raises(ValueError, match="constraint names"):
        Expression(
            variables=(x,),
            constraints=(
                Constraint(name="same", relation="eq", bound=0),
                Constraint(name="same", relation="eq", bound=1),
            ),
        )


def test_canonical_value_and_fingerprint_are_order_independent() -> None:
    first = {"b": {3, 1, 2}, "a": [1, 2]}
    second = {"a": [1, 2], "b": {2, 3, 1}}
    assert canonical_value(first) == canonical_value(second)
    assert fingerprint(first) == fingerprint(second)
    assert canonical_value(ValueType.BINARY) == "binary"
