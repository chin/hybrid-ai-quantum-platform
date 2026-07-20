from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import dimod

from optengine.formulations.base import (
    Formulation,
    Model,
)
from optengine.interpretation import (
    Interpretation,
    QuadraticBinaryInterpretation,
)


@dataclass(frozen=True, kw_only=True)
class QUBOModel(Model):
    payload: dimod.BinaryQuadraticModel
    coefficients: Mapping[
        tuple[Any, Any],
        float,
    ]


class QUBOFormulation(Formulation):
    name = "qubo"

    def supports(
        self,
        interpretation: Interpretation,
    ) -> bool:
        return isinstance(
            interpretation,
            QuadraticBinaryInterpretation,
        )

    def build(
        self,
        interpretation: Interpretation,
        configuration: Mapping[str, Any],
    ) -> Model:
        if not isinstance(
            interpretation,
            QuadraticBinaryInterpretation,
        ):
            raise TypeError("QUBO requires a quadratic binary interpretation.")

        multiplier = -1.0 if interpretation.objective_sense == "maximize" else 1.0

        coefficients: dict[
            tuple[Any, Any],
            float,
        ] = {}

        for variable, coefficient in interpretation.linear.items():
            coefficients[(variable, variable)] = multiplier * coefficient

        for pair, coefficient in interpretation.quadratic.items():
            coefficients[pair] = multiplier * coefficient

        bqm = dimod.BinaryQuadraticModel.from_qubo(
            coefficients,
            offset=multiplier * interpretation.offset,
        )

        return QUBOModel(
            formulation=self.name,
            payload=bqm,
            coefficients=coefficients,
            metadata={
                "objective_sense": (interpretation.objective_sense),
            },
        )
