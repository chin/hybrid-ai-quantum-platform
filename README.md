# OptEngine by OptChin

## A feasibility-aware modular optimization platform

**Quantifying operational optimality to simplify decision optionality**

OptEngine translates a business or research problem into a mathematical representation, maps that representation to interchangeable library-backed execution strategies, independently evaluates the results, and produces an evidence-grounded Stop/Switch/Scale recommendation.

OptEngine is not a replacement for optimization libraries. It composes and governs them.

## Implemented vertical slices

### Max-Cut reference workflow

```bash
make run
```

This executes:

```text
NetworkX graph
→ MaxCutDomain
→ quadratic binary interpretation
→ QUBO formulation
→ dimod exact solver and D-Wave local annealing
→ independent cut evaluation
→ OperationalUtilityModel
→ Stop/Switch/Scale
→ Recommendation JSON
```

### Bounded portfolio workflow

```bash
make portfolio
```

This executes:

```text
portfolio configuration
→ PortfolioDomain
→ bounded allocation interpretation
→ dimod CQM reference formulation
→ exact CQM execution and local-annealing QUBO execution
→ independent return/risk/constraint evaluation
→ OperationalUtilityModel
→ Stop/Switch/Scale
→ Recommendation JSON
```

The default business-readable configuration is [`config/examples/portfolio.json`](config/examples/portfolio.json). Results are written to `outputs/portfolio-vertical-slice_<timestamp>.json`.

## Bootstrap and common commands

```bash
make bootstrap          # Verify tools and synchronize the uv environment.
make run                # Run the Max-Cut vertical slice.
make portfolio          # Run the portfolio vertical slice.
make test               # Run the complete pytest suite.
make runtime-test       # Run runtime lifecycle and failure-path tests.
make regression-test    # Run the full suite with branch coverage.
make coverage           # Generate terminal and HTML coverage reports.
make dev                # Clean, format, test, lint, and build.
make artifact           # Run and promote a fresh Max-Cut output.
make portfolio-artifact # Run and promote a fresh portfolio output.
```

`make artifact` now runs the corresponding workflow first, so it does not depend on an output surviving `make dev` cleanup.

## Runtime components

| Component | Responsibility |
|---|---|
| `Domain` | Validates input, defines domain meaning, and independently evaluates candidates. |
| `Interpretation` | Stores variables, objective meaning, constraints, capabilities, and domain data. |
| `Formulation` | Builds a library-native mathematical model such as a BQM or CQM. |
| `Operation` | Describes the requested method, such as exact search or annealing. |
| Concrete `Solver` | Calls an existing library/backend and normalizes its native output. |
| `Candidate` | Contains solver-native values, score, telemetry, cost, and provenance. |
| `Evaluation` | Contains independently calculated feasibility, quality, and domain metrics. |
| `UtilityModel` | Converts evaluations into generic utility evidence. |
| `Policy` | Produces Stop, Switch, or Scale from utility evidence. |
| `Explainer` | Converts the structured decision into a grounded explanation. |
| `Recommendation` | Persists the complete run state, evidence, failures, and output path. |
| `OptEngine` | Holds the live collaborators and state for one execution. |
| `runner.run()` | Coordinates the lifecycle without containing domain-specific logic. |

## External-library boundary

```text
Domain Interpretation
→ Formulation
→ Concrete Solver
→ external library/backend
→ Candidate
```

External libraries own algorithm execution. OptEngine owns translation, composition, normalization, independent evaluation, utility, policy, explanation, and reproducibility.

Current adapters use:

- NetworkX for graph inputs;
- `dimod` for BQM/CQM models and exact solving;
- `dwave-samplers` for local simulated annealing.

The actual private OptChin utility mathematics is not yet connected. `OperationalUtilityModel` is the deterministic public fallback, and `OptChinUtilityAdapter` is the tested integration boundary.

## Create a new problem domain

Start with:

- [Problem Domain Creation Template](docs/problem-domain-template.md)
- [`templates/problem_domain.py`](templates/problem_domain.py)

The essential rule is:

```text
solver-native evidence belongs in Candidate
business/scientific meaning belongs in Domain Evaluation
```

## Create a repeatable execution

Use:

- [Execution Instance Template](docs/execution-instance-template.md)
- [`templates/execution_instance.py`](templates/execution_instance.py)
- [`optengine.execution.ExecutionInstance`](optengine/execution.py)

This allows researchers and decision-makers to define a named run without modifying the engine or runner.

## Outputs and curated artifacts

`outputs/` contains disposable timestamped run results. `artifacts/` contains deliberately promoted evidence with metadata.

```bash
make artifact
make portfolio-artifact
```

Promotion preserves the source output and gives each promoted run a unique timestamp-derived version.

## Verification

See [Testing and Verification](docs/testing.md). The suite verifies public runtime behavior, failure isolation, exact and annealing strategies, mathematical evaluation, utility and policy branches, JSON serialization, and portfolio execution.

## Documentation

- [Portfolio vertical slice](docs/portfolio-vertical-slice.md)
- [Problem domain template](docs/problem-domain-template.md)
- [Execution instance template](docs/execution-instance-template.md)
- [Testing and verification](docs/testing.md)
- [GitHub Project automation](docs/project-automation.md)
- [Detailed architecture](docs/detailed-architecture.md)
- [Mermaid architecture](docs/mermaid-architecture.md)
- [Release roadmap](docs/ROADMAP.md)
- [Makefile execution guide](docs/MAKEFILE.md)

## Deferred capabilities

AI may later propose interpretations, strategies, solver settings, warm starts, or explanations. Quantum backends may later provide additional concrete Solver implementations. Neither capability replaces deterministic constraint validation, independent evaluation, utility, or policy.

## License

OptEngine is licensed under the Apache License, Version 2.0. See [`LICENSE`](LICENSE).

Copyright © 2026 Chinyere "Chin" Isaac-Heslop.
