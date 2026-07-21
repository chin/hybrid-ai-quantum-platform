# Detailed Architecture

## Runtime invariant

The runner is domain-neutral. Adding portfolio, scheduling, logistics, scientific, or future quantum workflows must not require finance-, graph-, or backend-specific branches in `runner.py`.

## Execution lifecycle

1. `ExecutionInstance` or a direct caller invokes `optengine.run()`.
2. The Domain validates input and returns an `Interpretation`.
3. `StrategyRegistry` selects compatible strategy compositions.
4. Each Formulation builds a library-native `Model`.
5. Each concrete Solver executes the configured Operation through an external implementation.
6. Solver output is normalized into a `Candidate`.
7. The Domain independently interprets the Candidate into an `Evaluation`.
8. `UtilityModel` creates generic `UtilityAssessment` evidence.
9. `Policy` selects Stop, Switch, or Scale.
10. `Explainer` produces a grounded explanation.
11. `RecommendationWriter` writes the complete timestamped Recommendation.
12. Artifact promotion is a separate, explicit action.

## Contracts

### Domain

Owns input validity, mathematical meaning, independent feasibility, and domain metrics. It must not call solvers or trust native solver scores as final domain quality.

### Interpretation

Carries structured mathematical meaning and capabilities. Current interpretations include quadratic binary Max-Cut and bounded discrete portfolio allocation.

### Formulation

Builds a model for an existing library. Current models are `dimod.BinaryQuadraticModel` and `dimod.ConstrainedQuadraticModel`.

### Operation

Describes the method requested by a Strategy. Current operations are exact search and annealing.

### Concrete Solver

Validates model/operation compatibility, invokes the library, captures telemetry and provenance, and returns a Candidate.

### Candidate

Contains native sample values, native score, runtime, resource cost, native metrics, configuration metadata, and backend provenance. It does not contain independently calculated business/scientific judgments.

### Evaluation

Contains feasibility, quality, domain metrics, reference evidence, and generic utility inputs.

### Utility and policy

`OperationalUtilityModel` is the public deterministic fallback. `OptChinUtilityAdapter` is the future private OptChin integration boundary. The policy receives normalized evidence rather than domain-specific matrices, graphs, or assets.

### Recommendation

Contains the full persistent result: run identity, input summary, analysis, evaluations, utility assessment, decision, explanation, failures, provenance, logs, timestamps, and output path.

## Failure isolation

A Strategy runtime failure is recorded in `Recommendation.failures`; other selected strategies continue. Invalid static composition raises `IncompatibleStrategyError` before execution.

## Vertical slices

### Max-Cut

`MaxCutDomain → QUBOFormulation → DimodExactSolver/DWaveLocalSolver → independent cut evaluation`.

### Portfolio

`PortfolioDomain → PortfolioCQMFormulation/PortfolioQUBOFormulation → DimodCQMExactSolver/DWaveLocalSolver → independent return/risk/constraint evaluation`.

## Extension model

A new domain normally adds files only under `domains/`, `formulations/`, `solvers/`, `presets/`, `config/examples/`, `demos/`, and `tests/`. The engine, runner, Candidate, Evaluation, utility, policy, and Recommendation contracts should remain unchanged.

See the [Problem Domain Creation Template](problem-domain-template.md) and [Execution Instance Template](execution-instance-template.md).
