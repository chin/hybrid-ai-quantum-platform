from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Mapping

from optengine.operations.base import Operation
from optengine.mathematics import ValueType


@dataclass(frozen=True, kw_only=True)
class ExactSearch(Operation):
    name: ClassVar[str] = "exact-search"
    max_variables: int = 18

    def __post_init__(self) -> None:
        if self.max_variables <= 0:
            raise ValueError("max_variables must be positive.")

    @property
    def capability(self) -> Operation.Capability:
        return Operation.Capability(
            input_types=frozenset(
                {
                    ValueType.BINARY,
                    ValueType.INTEGER,
                }
            ),
            maximum_degree=2,
            supports_constraints=True,
            maximum_inputs=self.max_variables,
        )

    @property
    def configuration(self) -> Mapping[str, Any]:
        return {"max_variables": self.max_variables}


ExactSearchOperation = ExactSearch
