# Testing and Verification

## Quality gates

```bash
make test
make runtime-test
make contract-coverage
make coverage
make regression-test
make dev
make release-check
```

## Contract coverage

`make contract-coverage` requires **100% statement coverage** for the reusable
object collaboration contracts:

```text
Compatibility
Catalog
mathematical value objects
Domain base
Objective
Interpretation
Formulation and Model
Operation
Solver
Analysis and Analyzer
Strategy
Execution
Evaluation
Utility and Assessment
```

The gate excludes concrete third-party adapters from the 100% contract
threshold because those require their external libraries. They are covered by
separate integration tests.

## Reusable Domain contract

[`tests/contracts/domain.py`](../tests/contracts/domain.py) supplies the
extension harness. Every Domain test class provides:

```python
class TestNewDomainContract(DomainContract):
    def make_domain(self) -> Domain:
        ...

    def make_candidate(self, domain: Domain) -> Candidate:
        ...
```

The inherited tests verify:

- the Domain itself is the aggregate root;
- self-interpretation returns an idempotent `Interpretation`;
- Candidate interpretation is polymorphic and idempotent;
- uninterpretable objects fail explicitly;
- Candidates cannot cross Domain aggregate boundaries.

Concrete Domain tests then verify local entity, relationship, Objective,
Candidate, and Evaluation behavior.

## Test layers

### Mathematical value tests

`tests/test_mathematics.py` exhaustively verifies variables, terms,
constraints, expressions, Curves, deterministic canonicalization, and
fingerprints.

### Base collaboration tests

`tests/test_base_contracts.py` and
`tests/test_base_contract_coverage.py` verify nested capabilities, real-time
compatibility, Model filtering and decoding, Operation Request creation,
Solver Result normalization, Catalog identity, and default base behavior.

### Analysis and execution tests

`tests/test_analysis_execution.py` verifies N-strategy discovery,
compatibility evidence, requested-strategy ordering, deterministic
deduplication, successful execution, non-complete backend results, and failure
isolation.

### Utility and policy tests

`tests/test_utility_policy.py` verifies `OperationalUtility`,
`OptChinUtility`, deterministic Assessment ranking, reference gaps, failures,
and all Stop/Switch/Scale branches.

### Workflow tests

`tests/test_engine_workflow.py` verifies the stage order and complete
Recommendation artifact. One failing Strategy must not block successful
Strategies or prevent a Decision.

### Domain tests

- `tests/test_domain_maxcut.py`
- `tests/test_domain_portfolio.py`

These verify the concrete aggregate object graphs and domain-owned
interpretation behavior.

### External integration tests

`tests/test_external_integrations.py` verifies:

- Max-Cut QUBO exact execution;
- Portfolio CQM expression and exact execution;
- constrained Portfolio-to-QUBO conversion;
- seeded local annealing reproducibility.

Tests use `pytest.importorskip` when `dimod` or `dwave-samplers` is absent.
This allows contract development in a minimal environment while requiring
backend verification in the synchronized project environment.

### Architecture guardrails

`tests/test_architecture_guardrails.py` rejects:

- Domain-specific imports in the engine, runner, Analyzer, or stages;
- reintroduction of a separate `PortfolioInput`;
- top-level Capability, Request, or Result hierarchies that should be nested.

## Regression expectations

The test suite preserves:

- Max-Cut exact cut value and partition validity;
- seeded annealing reproducibility;
- Portfolio budget, one-choice, bounds, increment, and cardinality checks;
- multi-strategy generation;
- requested-strategy filtering;
- independent execution failures;
- utility ranking and reference gaps;
- all Stop/Switch/Scale decisions;
- CLI stage rendering;
- timestamped collision-safe JSON;
- artifact promotion safety;
- public imports;
- project-field automation.

## Dependency-complete verification

After applying the drop-in:

```bash
make bootstrap
make test
make contract-coverage
make run
make portfolio
make coverage
make release-check
```

The two demo commands prove the concrete `dimod` and `dwave-samplers`
execution paths in addition to the test suite.
