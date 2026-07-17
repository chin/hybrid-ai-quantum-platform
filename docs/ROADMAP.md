# OptEngine Roadmap at a Glance

## Planned Release Order

```text
v0.1.0 — Platform Foundation                         Published
v0.1.1 — Platform Foundation Closeout                Current
v0.2.0 — Portfolio Vertical-Slice MVP
v0.3.0 — AI Orchestration
v0.4.0 — Scientific AI and FNO Surrogates
v0.5.0 — Classical and Quantum Hybrid Optimization
v0.6.0 — Feasibility-Aware Decision Policy
v0.7.0 — Distributed HPC–Quantum Optimization
v0.8.0 — Research Validation and Evidence
v1.0.0 — Stable Validated Research Platform
```

| Release  | Purpose                                                      |
| -------- | ------------------------------------------------------------ |
| `v0.1.1` | Close documentation and artifact-registry foundation gaps    |
| `v0.2.0` | Prove the portfolio vertical slice and solver modularity     |
| `v0.3.0` | Extend the portfolio workflow into Vanguard hybrid execution |
| `v0.4.0` | Integrate the formal dissertation feasibility translation    |
| `v0.5.0` | Add AI orchestration and co-pilot behavior                   |
| `v0.6.0` | Add the Scientific-AI/FNO reference workflow                 |
| `v0.7.0` | Add distributed HPC–quantum execution                        |
| `v0.8.0` | Complete research validation and evidence packaging          |
| `v1.0.0` | Stabilize the validated OptEngine platform                   |

The development pattern is:

```text
prove one thin vertical slice
→ deepen AI orchestration through that slice
→ add a second scientific-AI slice
→ add classical/quantum backends to the working slice
→ replace the thin policy with the formal dissertation translation
→ distribute the working workflows
→ validate the complete platform
```

## GitHub object hierarchy

```text
GitHub Milestone
    One planned software release.

Feature Issue
    One capability that must ship in that release.

Sub-issue
    A separately trackable implementation, test, documentation, or research
    unit required by a feature.

Pull Request
    The reviewed change implementing or closing one or more issues.

Git tag + GitHub Release
    The immutable published result after the milestone is complete.
```

A milestone may also contain standalone `test:`, `docs:`, or `fix:` issues. Not every required release issue must be a feature.

---

## `v0.1.1 — Platform Foundation Closeout`

### Purpose

Finish the existing baseline documentation and artifact-safety work, then stop spending release cycles on general repository infrastructure.

### Milestone acceptance criteria

* [ ] Issues #5–#8 are closed
* [ ] README and documentation links are correct
* [ ] Both architecture formats render correctly
* [ ] Artifact promotion is non-destructive
* [ ] Artifact behavior has regression coverage
* [ ] `make dev` passes
* [ ] `make release-check` passes
* [ ] `v0.1.1` is published with release assets

---

## `v0.2.0 — Portfolio Vertical-Slice MVP`

### Purpose

Prove that OptEngine is a reusable optimization engine rather than a platform skeleton or hard-coded portfolio script.

### Milestone acceptance criteria

* [ ] Generic contracts are domain-neutral
* [ ] One portfolio problem executes end to end
* [ ] Exact baseline returns the known optimum
* [ ] Evaluation is solver-independent
* [ ] Stop/Switch/Scale is computed
* [ ] Reproducible evidence is emitted
* [ ] Two solvers prove modularity
* [ ] Fresh-clone execution succeeds
* [ ] `make dev` passes
* [ ] `make release-check` passes
* [ ] `v0.2.0` is published

---

## `v0.3.0 — AI Orchestration`

### Purpose

Replace deterministic stage selection with functional model, tool, and routing orchestration while keeping the portfolio workflow operational.

### Milestone acceptance criteria

* [ ] Registry is provider-neutral
* [ ] Routing is configuration-driven
* [ ] Switchyard is used only for model/tool orchestration
* [ ] Fallback behavior is tested
* [ ] Model and tool failures are explicit
* [ ] Routing provenance is recorded
* [ ] AI does not evaluate solver correctness
* [ ] AI does not make the final policy decision
* [ ] Deterministic non-AI execution remains supported
* [ ] Portfolio workflow still executes end to end
* [ ] `v0.3.0` is published

---

## `v0.4.0 — Scientific AI and FNO Surrogates`

### Purpose

Add a second reference workflow that genuinely requires scientific-surrogate evaluation.

### Milestone acceptance criteria

* [ ] Second domain uses the existing runner
* [ ] FNO is used only where operator learning is appropriate
* [ ] PhysicsNeMo sits behind a defined adapter
* [ ] Accuracy and uncertainty are measured
* [ ] Reference comparison is reproducible
* [ ] Failed or unacceptable surrogate behavior can trigger Switch
* [ ] Justified refinement can trigger Scale
* [ ] Accepted verified behavior can trigger Stop
* [ ] Portfolio-specific logic remains outside the core
* [ ] `v0.4.0` is published

---

## `v0.5.0 — Classical and Quantum Hybrid Optimization`

### Purpose

Expand the proven optimization path to multiple classical, QUBO, annealing, and gate-model backends.

### Milestone acceptance criteria

* [ ] Classical reference exists before quantum-benefit claims
* [ ] Max-Cut remains a controlled benchmark, not a universal formulation
* [ ] Portfolio QUBO is independently validated
* [ ] D-Wave and CUDA-Q remain adapters behind contracts
* [ ] Simulator, annealer, gate-model, and QPU evidence are distinguished
* [ ] Backends use the same evaluator
* [ ] Backend identity does not determine the policy action
* [ ] Objective, feasibility, runtime, cost, uncertainty, and reference gap are compared
* [ ] Vanguard round behavior maps to OptEngine iterations
* [ ] `v0.5.0` is published

---

## `v0.6.0 — Feasibility-Aware Decision Policy`

### Purpose

Replace the minimal MVP policy with the formal public translation of the dissertation-derived feasibility framework.

### Milestone acceptance criteria

* [ ] Policy contract is domain-neutral
* [ ] Private proofs and derivations remain outside the public repository
* [ ] Every decision is traceable to recorded evidence
* [ ] Stop, Switch, and Scale boundaries are independently tested
* [ ] Near-boundary behavior is tested
* [ ] Fixed evidence produces deterministic decisions
* [ ] Runner executes the returned policy action
* [ ] At least one portfolio and one scientific run use the formal adapter
* [ ] IP review is complete
* [ ] `v0.6.0` is published

---

## `v0.7.0 — Distributed HPC–Quantum Optimization`

### Purpose

Coordinate heterogeneous optimization and scientific workloads across distributed resources.

### Milestone acceptance criteria

* [ ] Working backend and evidence contracts already exist
* [ ] Decomposition boundaries are explicit
* [ ] Multiple tasks execute concurrently
* [ ] Partial failures do not corrupt completed evidence
* [ ] Timeouts and retries are bounded
* [ ] Aggregation is deterministic where required
* [ ] Resource and cost telemetry is retained
* [ ] Distributed metrics can drive Stop/Switch/Scale
* [ ] Distributed algorithms are implemented only where technically justified
* [ ] `v0.7.0` is published

---

## `v0.8.0 — Research Validation and Evidence`

### Purpose

Convert implemented capabilities into reproducible engineering, research, Vanguard, publication, and professional evidence.

### Milestone acceptance criteria

* [ ] Verification and validation are reported separately
* [ ] Benchmarks are reproducible
* [ ] Environment, version, seed, backend, and configuration are recorded
* [ ] Classical and hybrid comparisons use trusted references
* [ ] Stop/Switch/Scale behavior is validated across representative histories
* [ ] Failure and negative results are retained
* [ ] Every public technical claim maps to evidence
* [ ] Publication evidence includes methods, limitations, and provenance
* [ ] Security, licensing, privacy, and IP boundaries are reviewed
* [ ] `v0.8.0` is published

---

## `v1.0.0 — Stable Validated Research Platform`

### Purpose

Declare the supported OptEngine contracts, reference workflows, extensions, evidence, and release processes stable.

### Milestone acceptance criteria

* [ ] Public contracts are declared stable
* [ ] Compatibility and deprecation rules are published
* [ ] Clean installation is verified
* [ ] Portfolio workflow is supported
* [ ] Scientific-AI workflow is supported
* [ ] Classical and quantum/hybrid workflows are supported where claimed
* [ ] Formal feasibility-policy translation is integrated
* [ ] Distributed behavior is supported wherever advertised
* [ ] Benchmarks and validation procedures pass
* [ ] Artifacts and provenance are reproducible
* [ ] Extension guides are complete
* [ ] Security and release controls are verified
* [ ] No critical supported-workflow defect remains
* [ ] Unsupported planned capabilities remain labeled as planned
* [ ] `v1.0.0` is published with verified assets
