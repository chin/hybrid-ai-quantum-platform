# OptEngine by OptChin

## A feasibility-aware polymorphic optimization platform

**Quantifying operational optimality to simplify decision optionality**

OptEngine coordinates domain-owned problem meaning with interchangeable
formulations, operations, solvers, utility behavior, and Stop/Switch/Scale
policy. External libraries execute algorithms. OptEngine owns translation,
composition, independent domain evaluation, comparative assessment,
recommendation, and reproducible evidence.

## Quickstart

```bash
make run
```

The Max-Cut reference workflow is:

```text
MaxCut aggregate
→ Domain.interpret()
→ Objective
→ Expression
→ Curve
→ QUBO.express(Objective)
→ Model
→ ExactSearch / Annealing
→ DimodExact / DWaveLocal
→ Solver.Result
→ Model.decode()
→ MaxCut.Candidate
→ MaxCut.interpret(Candidate)
→ MaxCut.Evaluation
→ OperationalUtility.assess()
→ Assessment
→ Stop / Switch / Scale
→ Explanation
→ Recommendation
→ JSON
```

Run the bounded portfolio workflow with:

```bash
make portfolio
```

Its user-facing configuration is
[`config/examples/portfolio.json`](config/examples/portfolio.json).

## Architecture

The engine follows one invariant stage pattern:

```text
ANALYZE
  Domain.interpret()
  Formulation.express(Objective)
  Model filters compatible Operations
  Operation filters compatible Solvers
  Analysis returns N Strategies

EVALUATE
  each Strategy executes independently
  Operation.prepare(Model) returns Request
  Solver.execute(Request) returns Solver.Result
  Model.decode(Result) returns Domain Candidate
  Domain.interpret(Candidate) returns Domain Evaluation
  Execution records success or failure

DECIDE
  Utility.assess(Executions, Analysis) returns Assessment
  Policy.apply(Assessment) returns Stop, Switch, or Scale

EXPLAIN
  Explainer returns Explanation

WRITE
  Writer persists Recommendation
```

`OptEngine`, the runner, and the stages contain no Max-Cut or portfolio
branches. Compatibility is evaluated from the actual `Curve`: value types,
value counts, output types, degree, constraints, and limits. It is not selected
from a labeled objective type.

## Canonical object vocabulary

| Object | Responsibility |
|---|---|
| `Domain` | Aggregate root and owner of domain meaning. |
| `Objective` | Mathematical intent of the populated Domain. |
| `Expression` | Variables, terms, constraints, and constant. |
| `Curve` | Structural profile used for real-time compatibility. |
| `Formulation` | Polymorphic transformer with `express(Objective)`. |
| `Model` | Solver-oriented mathematical representation. |
| `Operation` | Algorithmic action prepared for a Model. |
| `Solver` | Concrete backend executor. |
| `Solver.Result` | Normalized native execution result. |
| `Strategy` | Immutable compatible Formulation/Model/Operation/Solver plan. |
| `Execution` | Immutable record of one isolated Strategy attempt. |
| `Candidate` | Domain-owned proposed output. |
| `Evaluation` | Domain-owned interpretation of a Candidate. |
| `Utility` | Behavior that compares executions. |
| `Assessment` | Persistent result produced by Utility. |
| `Policy` | Stop/Switch/Scale decision behavior. |
| `Decision` | `Stop`, `Switch`, or `Scale` value object. |
| `Explanation` | Human-readable evidence-grounded rationale. |
| `Recommendation` | Complete persistent workflow result. |

Capabilities are nested inside their owners:

```text
Formulation.Capability
Operation.Capability
Operation.Request
Solver.Capability
Solver.Result
```

Concrete extension names do not repeat their base type:

```text
QUBO(Formulation)
CQM(Formulation)
ExactSearch(Operation)
Annealing(Operation)
DimodExact(Solver)
DimodCQMExact(Solver)
DWaveLocal(Solver)
```

## Domain aggregates

The Domain object is the aggregate. There is no separate generic input
aggregate attached as `domain.input`.

```python
domain = MaxCut(
    name="triangle",
    graph=MaxCut.Graph(
        vertices=(...),
        edges=(...),
    ),
)
```

```python
portfolio = Portfolio(
    name="balanced",
    assets=(...),
    covariances=(...),
    parameters=Portfolio.Parameters(...),
)
```

Nested entities and relationships collaborate through object references. An
edge contains vertices; a covariance contains assets.

## Verification

```bash
make test               # Complete test suite.
make runtime-test       # Stages, execution isolation, utility, and policy.
make contract-coverage  # 100% coverage of reusable OOP contracts.
make coverage           # Complete repository coverage report.
make regression-test    # Full regression suite with branch coverage.
make dev                # Format and run the complete release-quality gate.
```

The reusable contract suite is deliberately domain-extensible through
[`tests/contracts/domain.py`](tests/contracts/domain.py).

External backend tests use `pytest.importorskip` so core contracts remain
testable even when `dimod` or `dwave-samplers` is not installed. A synchronized
development environment runs those integrations through `make test`.

## Commands

```bash
make bootstrap
make run
make portfolio
make test
make runtime-test
make contract-coverage
make coverage
make artifact
make portfolio-artifact
make dev
make release-check
```

## Documentation

- [Idempotent polymorphic OOP architecture](docs/idempotent-polymorphic-oop.md)
- [PR verification checklist](docs/PR_CHECKLIST_POLYMORPHIC_REFACTOR.md)
- [Verification report](docs/VERIFICATION_REPORT_POLYMORPHIC_REFACTOR.md)
- [Testing and verification](docs/testing.md)
- [Detailed architecture](docs/detailed-architecture.md)
- [Mermaid architecture](docs/mermaid-architecture.md)
- [Problem Domain extension guide](docs/problem-domain-template.md)
- [Execution Instance guide](docs/execution-instance-template.md)
- [Portfolio vertical slice](docs/portfolio-vertical-slice.md)
- [GitHub Project automation](docs/project-automation.md)
- [Release roadmap](docs/ROADMAP.md)

## External-library boundary

Current adapters use NetworkX for graph ingestion, `dimod` for BQM/CQM
construction and exact solving, and `dwave-samplers` for local simulated
annealing. The private OptChin mathematics can be connected through
`OptChinUtility`; `OperationalUtility` is the deterministic public
implementation. Both return the same `Assessment` contract.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).

Copyright © 2026 Chinyere "Chin" Isaac-Heslop.
