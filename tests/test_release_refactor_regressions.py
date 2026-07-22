from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from optengine.errors import IncompatibleStrategyError, MissingDependencyError
from optengine.identity import canonical_value, fingerprint, identifier_value
from optengine.trace import outcome_chain
from optengine.recommendation import Recommendation


@dataclass
class _FallbackValue:
    value: int


class _OpaqueIdentifier:
    def __repr__(self) -> str:
        return "opaque-id"


def test_error_objects_preserve_structured_context_and_messages() -> None:
    incompatible = IncompatibleStrategyError(
        strategy="s",
        formulation="f",
        operation="o",
        solver="v",
    )
    assert incompatible.strategy == "s"
    assert incompatible.formulation == "f"
    assert incompatible.operation == "o"
    assert incompatible.solver == "v"
    assert str(incompatible) == (
        "Incompatible strategy components: strategy='s', formulation='f', "
        "operation='o', solver='v'."
    )

    missing = MissingDependencyError("backend", "plugin")
    assert missing.dependency == "backend"
    assert missing.plugin == "plugin"
    assert str(missing) == "plugin requires the optional runtime dependency 'backend'."


def test_identity_fallbacks_are_deterministic_and_type_explicit() -> None:
    opaque = _OpaqueIdentifier()
    expected = {
        "type": f"{_OpaqueIdentifier.__module__}.{_OpaqueIdentifier.__qualname__}",
        "repr": "opaque-id",
    }
    assert canonical_value(opaque) == expected
    assert identifier_value(opaque) == expected
    assert fingerprint(opaque) == fingerprint(opaque)
    assert canonical_value(Path("a/b")) == "a/b"
    assert canonical_value(_FallbackValue(3)) == {'"value"': 3}


def test_outcome_chain_rejects_incomplete_recommendations() -> None:
    recommendation = Recommendation(
        run_id="r",
        domain_summary={},
        started_at="now",
        provenance={},
    )
    with pytest.raises(RuntimeError, match="no Assessment"):
        outcome_chain(recommendation)
