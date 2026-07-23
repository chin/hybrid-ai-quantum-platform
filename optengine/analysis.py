from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from optengine.catalog import Catalog
from optengine.compatibility import Compatibility
from optengine.domains.base import Domain
from optengine.errors import NoCompatibleStrategyError
from optengine.identity import fingerprint
from optengine.interpretation import Interpretation
from optengine.strategy import Strategy


@dataclass(frozen=True, kw_only=True)
class CompatibilityRecord:
    stage: str
    collaborator: str
    supported: bool
    reasons: tuple[str, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_result(
        cls,
        *,
        stage: str,
        collaborator: str,
        result: Compatibility,
    ) -> CompatibilityRecord:
        return cls(
            stage=stage,
            collaborator=collaborator,
            supported=result.supported,
            reasons=result.reasons,
            evidence=dict(result.evidence),
        )

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "stage": self.stage,
            "collaborator": self.collaborator,
            "supported": self.supported,
            "reasons": list(self.reasons),
            "evidence": dict(self.evidence),
        }


@dataclass(frozen=True, kw_only=True)
class Analysis:
    """Persistent and live result of polymorphic strategy discovery."""

    domain: Domain
    interpretation: Interpretation
    strategies: tuple[Strategy, ...]
    compatibility: tuple[CompatibilityRecord, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def strategy_names(self) -> tuple[str, ...]:
        return tuple(strategy.name for strategy in self.strategies)

    @property
    def fingerprint(self) -> str:
        return fingerprint(
            {
                "interpretation": self.interpretation.fingerprint,
                "strategies": [strategy.fingerprint for strategy in self.strategies],
                "catalog": dict(self.metadata),
            }
        )

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "fingerprint": self.fingerprint,
            "domain": dict(self.domain.summary),
            "interpretation": self.interpretation.to_dict(),
            "strategies": [strategy.summary() for strategy in self.strategies],
            "compatibility": [record.to_dict() for record in self.compatibility],
            "metadata": dict(self.metadata),
        }


class Analyzer:
    """Build every compatible Strategy without Domain-specific branching."""

    def analyze(
        self,
        domain: Domain,
        catalog: Catalog,
        requested: Sequence[str] | None = None,
    ) -> Analysis:
        interpretation = domain.interpret()
        if not isinstance(interpretation, Interpretation):
            raise TypeError("Domain self-interpretation must produce Interpretation.")

        objective = interpretation.objective
        records: list[CompatibilityRecord] = []
        strategies: list[Strategy] = []
        seen: set[str] = set()

        for formulation in catalog.formulations:
            formulation_result = formulation.compatibility(objective)
            records.append(
                CompatibilityRecord.from_result(
                    stage="formulation",
                    collaborator=formulation.name,
                    result=formulation_result,
                )
            )
            if not formulation_result:
                continue

            try:
                model = formulation.express(objective)
            except Exception as error:
                records.append(
                    CompatibilityRecord(
                        stage="expression",
                        collaborator=formulation.name,
                        supported=False,
                        reasons=(f"{type(error).__name__}: {error}",),
                    )
                )
                continue

            if model is None:
                records.append(
                    CompatibilityRecord(
                        stage="expression",
                        collaborator=formulation.name,
                        supported=False,
                        reasons=("Formulation returned no Model.",),
                    )
                )
                continue

            records.append(
                CompatibilityRecord(
                    stage="expression",
                    collaborator=formulation.name,
                    supported=True,
                    evidence={
                        "model": model.to_dict(),
                    },
                )
            )

            for operation in catalog.operations:
                operation_result = model.compatibility(operation)
                records.append(
                    CompatibilityRecord.from_result(
                        stage="operation",
                        collaborator=(f"{formulation.name}:{operation.name}"),
                        result=operation_result,
                    )
                )
                if not operation_result:
                    continue

                for solver in catalog.solvers:
                    solver_result = solver.compatibility(
                        operation=operation,
                        model=model,
                    )
                    records.append(
                        CompatibilityRecord.from_result(
                            stage="solver",
                            collaborator=(
                                f"{formulation.name}:{operation.name}:{solver.name}"
                            ),
                            result=solver_result,
                        )
                    )
                    if not solver_result:
                        continue

                    strategy = Strategy(
                        domain=domain,
                        formulation=formulation,
                        model=model,
                        operation=operation,
                        solver=solver,
                    )
                    if strategy.fingerprint in seen:
                        continue
                    seen.add(strategy.fingerprint)
                    strategies.append(strategy)

        if requested is not None:
            available = {strategy.name: strategy for strategy in strategies}
            unknown = tuple(name for name in requested if name not in available)
            if unknown:
                raise KeyError(
                    "Unknown or incompatible requested strategies: "
                    + ", ".join(unknown)
                )
            strategies = [available[name] for name in requested]

        if not strategies:
            raise NoCompatibleStrategyError("No compatible Strategy was discovered.")

        return Analysis(
            domain=domain,
            interpretation=interpretation,
            strategies=tuple(strategies),
            compatibility=tuple(records),
            metadata={
                "formulation_count": len(catalog.formulations),
                "operation_count": len(catalog.operations),
                "solver_count": len(catalog.solvers),
                "strategy_count": len(strategies),
            },
        )
