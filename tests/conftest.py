from __future__ import annotations

import pytest

from tests.support import (
    ExampleDomain,
    ExampleFormulation,
    ExampleOperation,
    ExampleSolver,
)


@pytest.fixture
def example_domain() -> ExampleDomain:
    return ExampleDomain()


@pytest.fixture
def example_formulation() -> ExampleFormulation:
    return ExampleFormulation()


@pytest.fixture
def example_operation() -> ExampleOperation:
    return ExampleOperation(limit=2)


@pytest.fixture
def example_solver() -> ExampleSolver:
    return ExampleSolver()
