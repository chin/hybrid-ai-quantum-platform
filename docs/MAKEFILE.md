# OptEngine Makefile Execution Guide

The Makefile is the supported developer interface for OptEngine. It keeps
execution, verification, artifact promotion, and release operations behind
stable commands while `tools/dev.py` centralizes the underlying tool calls.

## Command summary

| Command | Purpose | Source mutation | Disposable output |
|---|---|---:|---:|
| `make help` | List supported commands | No | No |
| `make bootstrap` | Verify tools and synchronize the `uv` environment | No | Environment only |
| `make run` | Run the Max-Cut reference workflow | No | `outputs/*.json` |
| `make portfolio` | Run the bounded portfolio workflow | No | `outputs/*.json` |
| `make test` | Run the complete pytest suite | No | Test caches |
| `make runtime-test` | Run stage, execution, Utility, and policy tests | No | Test caches |
| `make contract-coverage` | Require 100% coverage of reusable OOP contracts | No | Coverage data |
| `make coverage` | Run complete repository branch coverage | No | Coverage reports |
| `make regression-test` | Run the full regression suite with branch coverage | No | Coverage data |
| `make format` | Apply Ruff formatting | Yes | No |
| `make format-check` | Check Ruff formatting | No | No |
| `make lint` | Run Ruff static analysis | No | No |
| `make ci` | Run the non-mutating local CI gate | No | Test/coverage caches |
| `make dev` | Format, then run release readiness | Formatting only | Build/test products |
| `make build` | Build wheel and source distributions | No | `dist/`, build metadata |
| `make release-check` | Clean, run CI, and build | No | Rebuilt disposable products |
| `make version` | Preview the next semantic version and tag | No | No |
| `make release` | Dispatch the official GitHub release workflow | No | Remote release products |
| `make artifact` | Run and promote the latest Max-Cut output | Curated evidence | Output and artifact files |
| `make portfolio-artifact` | Run and promote the latest portfolio output | Curated evidence | Output and artifact files |
| `make clean` | Remove disposable outputs, caches, and build products | No | Deletes disposable files |
| `make docs` | Reserved documentation validation target | No | Not implemented |
| `make benchmark` | Reserved benchmark target | No | Not implemented |
| `make validate` | Reserved research-validation target | No | Not implemented |
| `make publish` | Reserved package-registry target | No | Not implemented |

## Execution workflows

### Reference workflows

```text
make run
└── bootstrap
    └── demos/quickstart.py
        └── timestamped Max-Cut Recommendation JSON

make portfolio
└── bootstrap
    └── demos/portfolio_vertical_slice.py
        └── timestamped portfolio Recommendation JSON
```

The demonstration commands execute the public OptEngine API. They do not
format source, run the test suite, or promote outputs automatically.

### Verification workflows

```text
make test
└── complete pytest suite

make runtime-test
├── analysis and Strategy discovery
├── independent Execution and failure isolation
├── stage orchestration
├── Utility → Assessment
└── Stop / Switch / Scale

make contract-coverage
└── 100% statement coverage for reusable contracts:
    ├── Compatibility and Catalog
    ├── mathematical value objects
    ├── Domain base contract
    ├── Objective and Interpretation
    ├── Formulation and Model
    ├── Operation and Request
    ├── Solver and Result
    ├── Analysis and Strategy
    ├── Execution and Evaluation
    └── Utility and Assessment

make coverage
└── complete repository branch-coverage report

make regression-test
└── full test tree with branch coverage
```

`make contract-coverage` is the extension-safety gate. It proves exhaustive
coverage of the domain-neutral object contracts that concrete Domains,
Formulations, Operations, Solvers, and Utilities extend. Concrete adapter
coverage is reported separately because optional external libraries may be
unavailable in a minimal environment.

### CI and development workflows

```text
make ci
└── bootstrap
    ├── status
    ├── format-check
    ├── lint
    ├── contract-coverage
    └── coverage

make dev
└── bootstrap
    ├── clean
    ├── format
    └── release-check
        ├── ci
        └── build

make release-check
└── bootstrap
    ├── clean
    ├── ci
    └── build
```

`make ci` is non-mutating with respect to tracked source. `make dev` is the
developer preparation path and may format source before running the same
verification gates.

## Command details

### `make bootstrap`

`bootstrap` verifies Python, Git, Make, and `uv`, then runs:

```bash
uv sync
```

This installs the declared development and runtime dependencies. Backend
integration tests and demos require the synchronized environment because they
use `dimod`, `dwave-samplers`, and NetworkX.

### `make run`

Runs the Max-Cut reference workflow:

```bash
make run
```

The workflow exercises:

```text
MaxCut
→ Objective
→ Expression
→ Curve
→ QUBO
→ ExactSearch and Annealing
→ DimodExact and DWaveLocal
→ Candidate
→ Evaluation
→ Utility
→ Assessment
→ Stop / Switch / Scale
→ Recommendation
```

### `make portfolio`

Runs the bounded portfolio workflow from
`config/examples/portfolio.json`:

```bash
make portfolio
```

The Domain is the aggregate root. The same engine stages execute without
portfolio-specific branching.

### `make test`

Runs all unit, contract, integration, regression, CLI, writer, artifact, and
project-automation tests:

```bash
make test
```

External backend tests use `pytest.importorskip`. In a synchronized environment
those tests execute; in a minimal environment they report explicit skips
instead of preventing core contract verification.

### `make runtime-test`

Runs the focused runtime set:

```bash
make runtime-test
```

The target covers real-time compatibility, N-Strategy analysis, isolated
execution, Utility assessment, policy decisions, rendering, and writing.

### `make contract-coverage`

Requires 100% coverage of reusable object contracts:

```bash
make contract-coverage
```

The target intentionally names domain-neutral modules and fails below 100%.
New concrete Domains should extend `tests/contracts/domain.py` rather than
copying the same aggregate and interpretation tests.

### `make coverage`

Runs complete package branch coverage and writes terminal and HTML reports:

```bash
make coverage
```

This report includes optional adapters. Its percentage can differ from the
contract gate when external backends are not installed.

### `make regression-test`

Runs all tests with branch coverage:

```bash
make regression-test
```

Use it when changing lifecycle behavior, compatibility, artifacts, public
imports, or output schemas.

### `make artifact` and `make portfolio-artifact`

Promotion is explicit and non-destructive:

```bash
make artifact
make portfolio-artifact
```

Each target first runs its workflow, then promotes the selected disposable
output into the curated artifact registry. Tests and CI never promote evidence
automatically.

### `make clean`

Removes disposable generated state while preserving tracked placeholders and
curated evidence. It is part of `make release-check`, not routine execution.

### `make release`

The release target requires:

- branch `main`;
- clean working tree;
- synchronized `origin/main`;
- authenticated GitHub CLI;
- a valid semantic-release preview.

It then dispatches `.github/workflows/release.yml`. The workflow remains a
manual operation rather than a push-triggered release.

## Recommended use

During implementation:

```bash
make test
make contract-coverage
```

Before updating a pull request:

```bash
make dev
```

Before a release:

```bash
make release-check
make version
make release
```

For the complete refactor verification sequence, use
[`PR_CHECKLIST_POLYMORPHIC_REFACTOR.md`](PR_CHECKLIST_POLYMORPHIC_REFACTOR.md).
