# OptEngine Development Roadmap

> Vertical-slice-first roadmap aligned with the mature object-collaboration architecture.

Related documents:

- [Detailed architecture](./detailed-architecture.md)
- [Mermaid architecture](./mermaid-architecture.md)

## 1. Roadmap objective

OptEngine will progress from a published platform foundation to a stable, validated, extensible optimization and scientific-computing platform.

The immediate architectural recovery path is:

```text
freeze current observable behavior
→ establish the Domain interpretation contract
→ establish Objective, Expression, and Curve
→ establish Formulation, Model, Operation, and Solver collaboration
→ migrate Max-Cut as the reference path
→ stabilize Strategy, Execution, Utility, Policy, and Recommendation
→ add Portfolio without engine branches
→ publish the Portfolio Vertical-Slice MVP
→ extend the working Portfolio path for Vanguard
```

Max-Cut is the **migration and compatibility proving ground**.

Portfolio is the **domain-neutrality acceptance test, product reference slice, and Vanguard foundation**.

## 2. Resolved release order

```text
v0.1.0 — Platform Foundation                         Published
v0.1.1 — Platform Foundation Closeout                Current
v0.2.0 — Portfolio Vertical-Slice MVP
v0.3.0 — Vanguard Hybrid Portfolio Extension
v0.4.0 — Dissertation Feasibility Translation
v0.5.0 — AI Orchestration and Co-Pilot
v0.6.0 — Scientific AI and FNO Reference Workflow
v0.7.0 — Distributed HPC–Quantum Execution
v0.8.0 — Research Validation and Evidence
v1.0.0 — Stable Validated OptEngine Platform
```

### Recommended deviation from the older roadmap

The older sequence placed horizontal AI, FNO, and general hybrid-backend expansion before a complete domain workflow.

The revised sequence prioritizes:

```text
real object collaboration
→ one preserved Max-Cut path
→ one new Portfolio path
→ Vanguard extension
→ later horizontal expansion
```

This is a deliberate dependency correction, not an accidental reorder.

## 3. Planning and tracking conventions

### 3.1 GitHub object hierarchy

```text
GitHub Milestone
    One planned software release.

Feature Issue
    One capability that must ship in that release.

Sub-issue
    A separately trackable implementation, test, documentation,
    research, or migration unit.

Pull Request
    The reviewed change implementing one or more issues.

Git tag and GitHub Release
    The immutable published result after milestone acceptance.
```

Checklist items and acceptance criteria remain inside an issue unless they need a separate pull request, owner, dependency, or completion decision.

### 3.2 Issue and commit naming

Use unscoped prefixes:

```text
feat:
fix:
test:
docs:
research:
chore:
```

Do not use parenthesized title scopes such as `feat(core):` unless repository automation is explicitly changed and verified.

Use labels for scope:

```text
initiative:vanguard

area:core
area:domain
area:mathematics
area:formulation
area:operation
area:solver
area:analysis
area:execution
area:utility
area:policy
area:artifacts
area:portfolio
area:submission

type:feature
type:test
type:docs
type:research

priority:P0
priority:P1
priority:P2
```

The GitHub milestone identifies the release; do not duplicate it with a release label.

## 4. Architectural release dependencies

```text
Domain semantics
    ↓
Objective, Expression, Curve
    ↓
Formulation and Model
    ↓
Operation and Solver capabilities
    ↓
Analysis and Strategy
    ↓
Execution and failure isolation
    ↓
Utility and Policy
    ↓
Explanation, Recommendation, Writer
    ↓
Second domain without engine changes
```

A later release must not bypass an earlier ownership boundary.

Examples:

- QAOA must execute a `Model` through an `Operation` and `Solver`; it must not interpret a `Domain` directly.
- AI may help assemble inputs or explain evidence; it must not grade its own solver output.
- The formal dissertation adapter must consume domain-neutral execution evidence; it must not be embedded in Portfolio.
- Distributed execution must preserve Strategy and Execution provenance rather than invent a separate result model.

---

# `v0.1.0 — Platform Foundation`

**Status:** Published

## Purpose

Establish the repository, package, execution shell, developer workflow, governance, artifact handling, and release infrastructure required for functional development.

## Preserved foundation

The next releases should extend or adapt the existing:

- centralized runner;
- execution context;
- returned solution/recommendation behavior;
- AI, optimization, and policy package boundaries;
- deterministic quickstart;
- JSON output path;
- Makefile development and release gates;
- CI and semantic-release workflow.

Do not replace these components without characterization evidence showing why adaptation is insufficient.

---

# `v0.1.1 — Platform Foundation Closeout`

**Status:** Current

## Purpose

Complete the documentation and artifact-safety work that protects the functional refactor, then stop spending release cycles on general repository infrastructure.

## High-level features

- [ ] Complete the platform-foundation README.
- [ ] Publish current-state detailed and Mermaid architecture documents.
- [ ] Publish this roadmap.
- [ ] Protect and verify non-destructive artifact promotion.
- [ ] Distinguish implemented, target, and deferred capabilities.
- [ ] Record the object-collaboration migration as the next release path.

## Acceptance criteria

- [ ] Existing issues `#5`–`#8` are closed or deliberately superseded.
- [ ] Architecture documents represent the same workflow and ownership model.
- [ ] Stop, Switch, and Scale control loops appear consistently.
- [ ] Artifact promotion rejects unsafe paths and overwrites.
- [ ] Artifact behavior has regression coverage.
- [ ] `make dev` passes.
- [ ] `make release-check` passes.
- [ ] `v0.1.1` is published with release assets.

---

# `v0.2.0 — Portfolio Vertical-Slice MVP`

## Purpose

Move OptEngine from a platform shell and unstable refactor to a real, reusable, end-to-end engine based on explicit object collaboration.

The release has two internal gates:

```text
Gate A — Max-Cut reference migration
    Prove the collaboration pattern while preserving known behavior.

Gate B — Portfolio domain acceptance
    Prove that a second domain can be added without engine branches.
```

Max-Cut is not the product endpoint. It is the safest reference slice for stabilizing the architecture before Portfolio.

## Gate 0 — Characterize the current implementation

- [ ] Record current test count, pass status, and coverage.
- [ ] Snapshot CLI section order.
- [ ] Capture Max-Cut exact output.
- [ ] Capture Max-Cut annealing invariants.
- [ ] Capture current Portfolio output, if present.
- [ ] Capture Recommendation JSON and artifact paths.
- [ ] Capture public imports and failure behavior.
- [ ] Normalize timestamps, UUIDs, runtimes, and temporary paths in snapshots.

### Acceptance criteria

- [ ] The refactor has a repeatable behavioral baseline.
- [ ] Failures can be attributed to an intentional change or a regression.

## Gate 1 — Domain and mathematical contracts

### Features

- [ ] Define the domain aggregate base contract.
- [ ] Implement the one-method, two-call interpretation API:

  ```python
  domain.interpret()
  domain.interpret(candidate)
  ```

- [ ] Use `typing.overload` and an omission sentinel.
- [ ] Keep explicit `None` distinct from an omitted argument.
- [ ] Define immutable `Interpretation` and domain-specific `Candidate`/`Evaluation` contracts.
- [ ] Define `Variable`, `Constraint`, `Expression`, `Objective`, and `Curve`.
- [ ] State that `Curve` is a compatibility profile, not a named problem or dissertation trajectory.
- [ ] Preserve deterministic and idempotent pure transformations.

### Acceptance criteria

- [ ] Both interpretation call forms are typed and tested.
- [ ] Explicit `None` follows candidate validation rather than aggregate interpretation.
- [ ] No core engine code imports a concrete domain.
- [ ] Equivalent domain aggregates produce equivalent interpretations and curves.
- [ ] Invalid domain states fail explicitly.

## Gate 2 — Formulation and Model collaboration

### Features

- [ ] Implement `Formulation.express(Objective) -> Model | None`.
- [ ] Define nested `Formulation.Capability`.
- [ ] Define immutable `Model`.
- [ ] Preserve source objective and source curve.
- [ ] Expose the formulated target curve.
- [ ] Record transformation metadata.
- [ ] Keep candidate decoding inside `Model`.
- [ ] Give each model a stable fingerprint.
- [ ] Add temporary aliases for replaced public names.

### Acceptance criteria

- [ ] Formulations inspect mathematical structure rather than domain names.
- [ ] Unsupported curves are rejected without concrete-domain branches.
- [ ] Structure-changing formulations expose a correct target curve.
- [ ] Operations and solvers inspect the target curve.
- [ ] `Model.decode()` returns a domain candidate but does not evaluate it.

## Gate 3 — Operation, Solver, Catalog, and Strategy collaboration

### Features

- [ ] Define nested `Operation.Capability`.
- [ ] Define nested `Solver.Capability`.
- [ ] Implement `Model.operations(catalog.operations)`.
- [ ] Implement `Operation.solvers(model, catalog.solvers)`.
- [ ] Preserve solver availability and size limits.
- [ ] Define injected `Catalog`.
- [ ] Retain immutable `Strategy`.
- [ ] Include model, operation, solver, configuration, seed, and budget in strategy identity.
- [ ] Deduplicate strategies deterministically.
- [ ] Preserve requested-strategy filtering and budget propagation.

### Acceptance criteria

- [ ] Plugins are filtered polymorphically.
- [ ] Models and operations do not instantiate concrete plugins.
- [ ] Analysis can produce zero, one, or many strategies.
- [ ] Equivalent strategy inputs produce equivalent fingerprints.
- [ ] Compatibility-matrix tests cover supported and unsupported combinations.

## Gate 4 — Execution, Utility, Policy, and Recommendation

### Features

- [ ] Execute every strategy independently.
- [ ] Preserve runtime, native result, candidate, evaluation, failure, and provenance.
- [ ] Convert failures into failed `Execution` records.
- [ ] Introduce first-class immutable `Utility`.
- [ ] Keep `UtilityModel` as swappable behavior.
- [ ] Preserve `OperationalUtilityModel` through an adapter or compatibility alias.
- [ ] Compute metric-derived Stop, Switch, and Scale decisions.
- [ ] Define bounded Switch and Scale loops.
- [ ] Produce an evidence-grounded explanation.
- [ ] Return a complete immutable `Recommendation`.
- [ ] Preserve external JSON keys during the internal migration.

### Acceptance criteria

- [ ] One failed strategy does not terminate other strategies.
- [ ] Utility consumes complete executions rather than only domain evaluations.
- [ ] Solver identity alone never determines policy action.
- [ ] Stop, Switch, and Scale fixtures are independently tested.
- [ ] Recommendation includes analysis, executions, utility, decision, and explanation.
- [ ] Writer serialization is deterministic for equivalent evidence.

## Gate A — Max-Cut reference migration

### Features

- [ ] Build `MaxCut` as a domain aggregate of `Vertex` and `Edge` objects.
- [ ] Implement `MaxCut.interpret()` as a binary quadratic objective.
- [ ] Implement `MaxCut.interpret(candidate)` as independent cut evaluation.
- [ ] Express the objective through QUBO.
- [ ] Support the existing exact strategy.
- [ ] Preserve an annealing strategy where already operational.
- [ ] Decode native results through `Model`.
- [ ] Record cut value, partitions, crossing edges, and feasibility.
- [ ] Compare old and new paths against identical fixtures.

### Acceptance criteria

- [ ] Exact Max-Cut output remains equivalent to the characterized baseline.
- [ ] Annealing candidates satisfy declared invariants.
- [ ] At least two compatible strategies can be represented without runner branches.
- [ ] Strategy provenance and fingerprints are retained.
- [ ] The complete Max-Cut workflow produces a Recommendation and artifact.

## Gate B — Portfolio domain acceptance

### Features

- [ ] Build `Portfolio` as a domain aggregate with object-referenced relationships.
- [ ] Define a bounded deterministic portfolio fixture.
- [ ] Implement Portfolio aggregate and candidate interpretation.
- [ ] Produce a constrained quadratic source objective.
- [ ] Implement a bounded exact or trusted classical reference path.
- [ ] Evaluate return, risk, transaction cost, concentration, constraints, and feasibility independently.
- [ ] Use the shared Strategy, Execution, Utility, Policy, Recommendation, and Writer flow.
- [ ] Add Portfolio without modifying engine orchestration.

### Acceptance criteria

- [ ] Portfolio introduces no concrete-domain branch in the engine.
- [ ] The bounded fixture returns the known optimum.
- [ ] Solver and domain evaluation remain separate.
- [ ] The same utility and policy contracts work for Max-Cut and Portfolio.
- [ ] Portfolio produces a reproducible Recommendation artifact.
- [ ] A polymorphism test fails if core engine modules import Max-Cut or Portfolio.

## Release evidence and usability

- [ ] Validate contract tests for every concrete plugin.
- [ ] Validate compatibility tests for representative curves.
- [ ] Validate failure isolation.
- [ ] Validate overload semantics and omission-versus-`None` behavior.
- [ ] Validate public imports and compatibility aliases.
- [ ] Validate fresh-clone bootstrap and execution.
- [ ] Publish Max-Cut migration and Portfolio quickstart documentation.
- [ ] Document limitations and deferred features.

## Milestone acceptance criteria

- [ ] The mature collaboration chain executes end to end.
- [ ] Max-Cut preserves established behavior.
- [ ] Portfolio is added without engine changes.
- [ ] Multiple compatible strategies use common contracts.
- [ ] Domain evaluation, utility assessment, and policy remain separate.
- [ ] Failed executions are retained without corrupting successful evidence.
- [ ] Recommendation artifacts are reproducible and safely promotable.
- [ ] `make dev` passes.
- [ ] `make release-check` passes.
- [ ] `v0.2.0` is published.

## Minimum executable recovery checkpoint

Before every release criterion is complete, the first honest executable checkpoint is:

```text
MaxCut aggregate
→ Domain.interpret()
→ Objective / Expression / Curve
→ QUBO.express()
→ Model
→ ExactSearch / Solver
→ Model.decode()
→ Domain.interpret(candidate)
→ Execution
→ Utility
→ Decision
→ Recommendation
→ JSON artifact
```

This checkpoint is an enabling prototype, not the full `v0.2.0` release.

---

# `v0.3.0 — Vanguard Hybrid Portfolio Extension`

## Purpose

Extend the proven Portfolio domain and shared collaboration contracts into the complete Vanguard classical-to-quantum reference application.

## Object-collaboration expansion

```text
Portfolio Domain Objective
├── Continuous constrained Formulation
├── CQM Formulation
└── Penalty-QUBO Formulation

Model
├── ContinuousOptimization Operation
├── Exact or heuristic discrete Operation
├── Annealing Operation
└── QAOA Operation

Solver adapters
├── trusted classical continuous solver
├── classical QUBO/CQM validator
├── annealing simulator or backend
└── gate-model simulator or backend
```

## High-level features

- [ ] Implement and validate a continuous mean-variance baseline.
- [ ] Compare continuous and bounded/discretized Portfolio objectives.
- [ ] Implement CQM and/or penalty-QUBO formulation.
- [ ] Record source-to-target curve transformations.
- [ ] Implement classical QUBO/CQM validation before quantum claims.
- [ ] Implement at least one quantum or hybrid solver adapter.
- [ ] Distinguish simulator, annealer, gate-model, and QPU evidence.
- [ ] Compare objective, feasibility, reference gap, runtime, resource cost, uncertainty, and policy decision.
- [ ] Produce reproducible benchmark tables and artifacts.
- [ ] Publish the Vanguard evidence package, report, presentation, and prototype.

## Acceptance criteria

- [ ] The continuous baseline is independently validated.
- [ ] The discrete formulation is classically validated.
- [ ] Constraint transformations and penalties are reproducible.
- [ ] Every backend passes through the same Portfolio interpretation and utility pipeline.
- [ ] Backend identity does not dictate Stop, Switch, or Scale.
- [ ] Classical and quantum/hybrid results are compared without unsupported advantage claims.
- [ ] Vanguard presentation claims map to actual tests and artifacts.
- [ ] `v0.3.0` is published.

---

# `v0.4.0 — Dissertation Feasibility Translation`

## Purpose

Replace the minimal operational utility and policy rules with the formal public translation between execution evidence and the dissertation-derived feasibility framework.

## Object ownership

The formal translation belongs behind `UtilityModel` and `Policy` adapters.

It does not belong inside:

- Max-Cut;
- Portfolio;
- Formulation;
- Solver;
- Writer.

## High-level features

- [ ] Define the public normalized execution-evidence contract.
- [ ] Define the public/private theory adapter boundary.
- [ ] Translate admissibility, feasibility, cost, utility, and marginal value.
- [ ] Preserve domain-neutral inputs.
- [ ] Implement formal Stop, Switch, and Scale boundaries.
- [ ] Execute returned Switch and Scale actions through the engine loop.
- [ ] Validate boundary and near-boundary behavior.
- [ ] Preserve public decision evidence without exposing private derivations.
- [ ] Use the formal adapter for at least one Max-Cut and one Portfolio run.

## Acceptance criteria

- [ ] Equivalent evidence produces equivalent utility and decisions.
- [ ] Every decision is traceable to recorded execution evidence.
- [ ] Private proofs and unpublished derivations remain outside the public repository.
- [ ] Public interfaces contain sufficient operational evidence.
- [ ] Iterative policy actions are bounded and replayable.
- [ ] IP review is complete.
- [ ] `v0.4.0` is published.

---

# `v0.5.0 — AI Orchestration and Co-Pilot`

## Purpose

Add model, agent, and tool orchestration without allowing AI to replace deterministic domain interpretation, solver evaluation, utility assessment, or policy authority.

## Object-collaboration placement

AI may assist with:

- raw-input interpretation before Domain aggregate construction;
- configuration and catalog discovery;
- natural-language explanation of structured evidence;
- tool and model routing;
- portfolio co-pilot interaction.

AI must not:

- fabricate Domain evaluations;
- grade its own solver output;
- override `UtilityModel` evidence;
- make the final feasibility decision.

## High-level features

- [ ] Implement provider-neutral model and tool registry.
- [ ] Implement configuration-driven routing and deterministic fallback.
- [ ] Integrate local, NIM, cloud, and tool adapters behind contracts.
- [ ] Record routing identity, rationale, and provenance.
- [ ] Integrate AI-assisted domain-input assembly with validation.
- [ ] Implement evidence-grounded Portfolio co-pilot explanations.
- [ ] Preserve deterministic non-AI workflows.

## Acceptance criteria

- [ ] Runner logic contains no provider-specific conditions.
- [ ] Fallback behavior is tested.
- [ ] Model and tool failures are explicit.
- [ ] AI output remains traceable to structured evidence.
- [ ] Portfolio and Max-Cut still execute without AI.
- [ ] `v0.5.0` is published.

---

# `v0.6.0 — Scientific AI and FNO Reference Workflow`

## Purpose

Prove that the collaboration model supports a scientific surrogate domain and trainable/inference operations without contaminating the optimization domains or core engine.

## Object-collaboration expansion

The scientific branch may require explicit extensions such as:

- structured tensor or field value types;
- dataset and reference-solution contracts;
- scientific `Objective`, `Expression`, or compatibility profiles;
- training and inference operations;
- checkpoint-aware models;
- accelerator and uncertainty evidence.

These extensions must be driven by the real workflow, not speculative abstractions added during `v0.2.0`.

## High-level features

- [ ] Define scientific domain and dataset aggregates.
- [ ] Define trusted high-fidelity reference evidence.
- [ ] Implement a baseline FNO workflow.
- [ ] Implement PhysicsNeMo behind a solver/runtime adapter.
- [ ] Record accuracy, error, uncertainty, runtime, and resource cost.
- [ ] Compare surrogate and reference results reproducibly.
- [ ] Feed complete scientific executions into the same utility and policy contracts.
- [ ] Trigger Stop, Switch, or Scale from scientific evidence.

## Acceptance criteria

- [ ] A scientific domain uses the existing engine workflow.
- [ ] Scientific extensions do not introduce Portfolio or Max-Cut branches.
- [ ] FNO behavior is validated against a trusted reference.
- [ ] Accuracy and uncertainty are explicit.
- [ ] Failed or unacceptable surrogates can trigger Switch.
- [ ] Justified refinement can trigger Scale.
- [ ] Accepted verified behavior can trigger Stop.
- [ ] `v0.6.0` is published.

---

# `v0.7.0 — Distributed HPC–Quantum Execution`

## Purpose

Coordinate multiple strategy executions across heterogeneous resources while retaining the same immutable strategy, execution, utility, policy, and recommendation contracts.

## Object-collaboration expansion

Distributed work should decompose and schedule **Strategies or declared sub-strategy tasks**, not bypass the collaboration model.

Strategy fingerprints become idempotency and provenance keys for remote execution.

## High-level features

- [ ] Define distributed task, workload, resource, status, partial-result, and aggregation contracts.
- [ ] Decompose workloads at explicit boundaries.
- [ ] Schedule and execute tasks concurrently.
- [ ] Bound retries, timeouts, and resource use.
- [ ] Preserve completed and partial execution evidence.
- [ ] Aggregate results deterministically where required.
- [ ] Record HPC, QPU, accelerator, and network resource costs.
- [ ] Feed distributed telemetry into Utility and Policy.
- [ ] Assess distributed quantum methods before implementation.

## Acceptance criteria

- [ ] Multiple tasks execute concurrently.
- [ ] Duplicate remote submissions can be prevented using fingerprints where supported.
- [ ] Partial failures do not corrupt completed evidence.
- [ ] Aggregated executions remain traceable to original strategies.
- [ ] Distributed metrics can drive Stop, Switch, and Scale.
- [ ] Distributed algorithms are implemented only where justified.
- [ ] `v0.7.0` is published.

---

# `v0.8.0 — Research Validation and Evidence`

## Purpose

Convert implemented collaborations into reproducible engineering, Vanguard, dissertation, publication, resume, and professional-launch evidence.

## High-level features

- [ ] Define versioned experiment and result schemas.
- [ ] Implement a reproducible benchmark suite.
- [ ] Validate repeatability, idempotency, and seeded behavior.
- [ ] Publish an evidence-backed comparison dashboard.
- [ ] Publish executable Max-Cut, Portfolio, Vanguard, scientific, and policy demonstrations.
- [ ] Maintain an engineering evidence ledger.
- [ ] Map public claims to tests, artifacts, benchmarks, versions, and limitations.
- [ ] Publish the experimental reproducibility protocol.
- [ ] Complete licensing, security, privacy, and IP review.

## Required verification layers

- [ ] Characterization tests.
- [ ] Contract tests.
- [ ] Curve/plugin compatibility tests.
- [ ] Domain polymorphism tests.
- [ ] Failure-isolation tests.
- [ ] Public API tests.
- [ ] Overload and omission-sentinel tests.
- [ ] Artifact-schema and promotion tests.
- [ ] Research validation against trusted references.

## Acceptance criteria

- [ ] Verification and validation are reported separately.
- [ ] Environment, version, seed, strategy, backend, and configuration are recorded.
- [ ] Failure and negative results are retained.
- [ ] Every public technical claim maps to evidence.
- [ ] Resume, LinkedIn, and publication statements do not exceed implemented evidence.
- [ ] Security, licensing, privacy, and IP boundaries are reviewed.
- [ ] `v0.8.0` is published.

---

# `v1.0.0 — Stable Validated OptEngine Platform`

## Purpose

Declare the supported collaboration contracts, reference workflows, extension mechanisms, evidence, and release processes stable for external use and continued research.

## High-level features

- [ ] Stabilize Domain, Interpretation, Objective, Expression, Curve, Formulation, Model, Operation, Solver, Strategy, Execution, Utility, Policy, Recommendation, and artifact contracts.
- [ ] Publish compatibility and deprecation policy.
- [ ] Verify fresh-clone, wheel, and source-distribution installation.
- [ ] Support every advertised reference workflow end to end.
- [ ] Publish domain, formulation, operation, solver, utility, policy, and writer extension guides.
- [ ] Verify security, protected-branch, artifact, provenance, and release controls.
- [ ] Resolve critical defects in supported workflows.
- [ ] Publish no-regression capability coverage.

## Acceptance criteria

- [ ] Public contracts are documented and declared stable.
- [ ] Compatibility and migration expectations are explicit.
- [ ] Max-Cut, Portfolio, Vanguard, scientific, and formal-policy workflows execute where advertised.
- [ ] Multiple domains and plugins collaborate without engine branches.
- [ ] Quantum and hybrid claims are validated against trusted classical references.
- [ ] Benchmarks and artifacts are reproducible.
- [ ] Extension guides are complete.
- [ ] Unsupported capabilities remain labeled as planned.
- [ ] `v1.0.0` is published with verified assets.

---

# Architecture-to-release mapping

| Architectural capability | First release target |
|---|---|
| Domain interpretation overload and aggregate pattern | `v0.2.0` |
| Objective, Expression, Curve | `v0.2.0` |
| Formulation and immutable Model | `v0.2.0` |
| Operation/Solver capabilities and Catalog | `v0.2.0` |
| Strategy fingerprints and N-strategy Analysis | `v0.2.0` |
| Failure-isolated Execution | `v0.2.0` |
| Utility, minimal Policy, Recommendation | `v0.2.0` |
| Max-Cut migration and Portfolio domain acceptance | `v0.2.0` |
| Portfolio continuous, CQM/QUBO, quantum/hybrid comparison | `v0.3.0` |
| Formal dissertation UtilityModel and Policy adapters | `v0.4.0` |
| AI registry, routing, input assistance, co-pilot | `v0.5.0` |
| FNO and scientific surrogate reference workflow | `v0.6.0` |
| Distributed strategy execution and aggregation | `v0.7.0` |
| Full research validation and professional evidence | `v0.8.0` |
| Stable supported public platform | `v1.0.0` |

# Vanguard-to-OptEngine mapping

| Vanguard requirement | OptEngine collaboration |
|---|---|
| Portfolio definition | `Portfolio` Domain aggregate |
| Risk/return/cost objective | `Portfolio.interpret() → Objective` |
| Continuous classical baseline | Continuous `Formulation → Model → Operation → Solver` |
| Binary/QUBO formulation | Penalty-QUBO `Formulation` |
| Classical QUBO validation | Classical discrete `Operation/Solver` |
| Quantum/hybrid implementation | Annealing or QAOA `Operation/Solver` |
| Decode allocation | `Model.decode()` |
| Evaluate constraints and metrics | `Portfolio.interpret(candidate)` |
| Compare backends | `UtilityModel.assess(Execution[])` |
| Stop/Switch/Scale | `Policy.apply(Utility)` |
| Explain recommendation | `Explainer` and `Recommendation` |
| Reproducibility | Strategy fingerprints and artifacts |

# Dissertation-to-OptEngine mapping

| Dissertation concept | Public software placement |
|---|---|
| Candidate admissibility | Domain candidate interpretation and evaluation evidence |
| Feasibility recognition | Formal policy adapter in `v0.4.0` |
| Execution cost | `Execution` resource evidence |
| Utility and marginal value | `UtilityModel` |
| Stop/Switch/Scale boundaries | `Policy` |
| Iterative control | Engine loop using new Strategy fingerprints |
| Public/private boundary | Adapter contract and IP-reviewed implementation |

The public repository should expose operational contracts and recorded evidence without publishing private proofs or unpublished derivations.

# Verification versus validation

## Verification

Answers:

> Did the software implement its declared contracts correctly?

Examples:

- overload dispatch;
- candidate decoding;
- compatibility filtering;
- deterministic fingerprints;
- failure isolation;
- artifact schema;
- CLI and public API behavior.

## Validation

Answers:

> Does the implemented workflow provide credible results for its intended problem?

Examples:

- Max-Cut exact result against a known optimum;
- Portfolio result against a trusted classical baseline;
- QUBO decoding against the source objective;
- quantum/hybrid comparison against classical references;
- FNO output against high-fidelity evidence;
- formal policy behavior against declared scenarios.

Verification and validation must be reported separately.

# Enabling prototype versus supported capability

A component may appear in a working demonstration before it is declared supported.

## Enabling prototype

- exercises the collaboration path;
- may have narrow fixtures and limits;
- is clearly marked experimental;
- cannot support broad performance or research claims.

## Supported capability

- has documented contracts and limitations;
- passes contract, integration, and regression tests;
- has reproducible evidence;
- has compatibility and failure behavior defined;
- is included in release acceptance.

The Max-Cut minimum executable checkpoint is an enabling prototype until the complete `v0.2.0` release gate passes.

# Immediate static execution order

- [ ] Freeze current observable behavior.
- [ ] Define the Domain aggregate and overload convention.
- [ ] Define Objective, Expression, and Curve.
- [ ] Define Formulation and Model with source/target curves.
- [ ] Define Operation and Solver capabilities.
- [ ] Retain Strategy and implement stable fingerprints.
- [ ] Port Max-Cut interpretation, QUBO expression, decoding, and evaluation.
- [ ] Restore one exact end-to-end Recommendation path.
- [ ] Restore or add a second compatible strategy.
- [ ] Replace Analysis internals without domain branches.
- [ ] Replace Execution and Utility internals with failure isolation.
- [ ] Preserve external JSON, CLI, artifacts, and public imports.
- [ ] Port Portfolio without changing engine orchestration.
- [ ] Pass the `v0.2.0` release gate.
- [ ] Publish `v0.2.0`.
- [ ] Implement the Vanguard continuous and discrete formulations.
- [ ] Validate the portfolio QUBO/CQM classically.
- [ ] Implement the first quantum or hybrid backend.
- [ ] Publish `v0.3.0` and the Vanguard evidence package.
- [ ] Integrate the formal dissertation adapter.
- [ ] Integrate AI orchestration and co-pilot behavior.
- [ ] Add the scientific FNO reference workflow.
- [ ] Add distributed execution.
- [ ] Complete validation and evidence packaging.
- [ ] Stabilize and publish `v1.0.0`.

# Explicit deferred scope during `v0.2.0`

- FNO, PINN, and QAPINN implementations;
- production QPU execution;
- distributed scheduling;
- AI-controlled correctness or feasibility;
- formal private dissertation derivations;
- full Vanguard submission evidence;
- dashboard and notebook suite;
- breaking artifact-schema changes;
- speculative trainable-model abstractions not required by Max-Cut or Portfolio.
