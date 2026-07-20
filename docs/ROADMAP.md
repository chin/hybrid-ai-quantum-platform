# OptEngine Roadmap


## Roadmap at a Glance

| Release | Status | Purpose |
|---|---|---|
| `v0.1.0 — Platform Foundation` | Published | Establish the repository, package, execution lifecycle, development workflow, governance, and release foundation |
| `v0.1.1 — Platform Foundation Closeout` | Current | Close documentation and artifact-registry foundation gaps |
| `v0.2.0 — Portfolio Vertical-Slice MVP` | Planned | Prove an end-to-end portfolio workflow, domain-neutral contracts, and solver modularity |
| `v0.3.0 — AI Orchestration` | Planned | Add functional model, tool, and routing orchestration to the working portfolio slice |
| `v0.4.0 — Scientific AI and FNO Surrogates` | Planned | Add a second scientific reference workflow using appropriate surrogate evaluation |
| `v0.5.0 — Classical and Quantum Hybrid Optimization` | Planned | Extend the working optimization path to classical, QUBO, annealing, and gate-model backends |
| `v0.6.0 — Feasibility-Aware Decision Policy` | Planned | Replace the minimal MVP policy with the formal public dissertation-feasibility translation |
| `v0.7.0 — Distributed HPC–Quantum Optimization` | Planned | Extend supported workflows across distributed and heterogeneous resources |
| `v0.8.0 — Research Validation and Evidence` | Planned | Complete reproducible validation, benchmarking, evidence, and publication support |
| `v1.0.0 — Stable Validated Research Platform` | Planned | Stabilize the supported OptEngine platform, contracts, workflows, and evidence |

## Capability Progress

### Core Platform

- [x] Repository and Python package structure
- [x] Centralized execution runner
- [x] Shared execution context
- [x] Returned solution contract
- [x] AI, optimization, and policy package boundaries
- [x] Deterministic quickstart
- [x] CLI and runtime presentation
- [x] CI, testing, packaging, and semantic releases
- [x] Protected `main` and repository ownership
- [ ] Complete platform-foundation documentation
- [ ] Verify and protect curated artifact behavior

### Portfolio Vertical Slice

- [ ] Domain-neutral execution contracts
- [ ] Portfolio problem adapter
- [ ] Portfolio input and constraint validation
- [ ] Deterministic exact portfolio baseline
- [ ] Independent portfolio evaluator
- [ ] Generic policy-input translation
- [ ] Computed Stop/Switch/Scale decisions
- [ ] Reproducible run evidence
- [ ] End-to-end portfolio workflow
- [ ] Second solver proving modularity
- [ ] Configuration-driven solver selection
- [ ] Fresh-clone MVP validation

### AI Orchestration

- [ ] Model and tool registry
- [ ] Deterministic local routing
- [ ] Configuration-driven routing and fallback
- [ ] NeMo Switchyard integration
- [ ] Supported local, NIM, and cloud adapters
- [ ] Code-agent and tool invocation
- [ ] Routing provenance
- [ ] AI-routed portfolio reference workflow

### Scientific AI

- [ ] Scientific problem and dataset contracts
- [ ] Trusted reference dataset or solver
- [ ] Baseline FNO workflow
- [ ] PhysicsNeMo integration
- [ ] Accuracy, uncertainty, and cost analytics
- [ ] High-fidelity reference comparison
- [ ] Surrogate-driven Stop/Switch/Scale behavior
- [ ] Scientific reference workflow

### Classical and Quantum Hybrid Optimization

- [ ] Generic optimization-backend contract
- [ ] Controlled Max-Cut QUBO benchmark
- [ ] Portfolio QUBO formulation
- [ ] Classical QUBO validator
- [ ] D-Wave Ocean integration
- [ ] CUDA-Q and QAOA integration
- [ ] Simulator, annealer, gate-model, and QPU distinction
- [ ] Backend-independent evaluation
- [ ] Hybrid search and fallback
- [ ] Vanguard comparative evidence package

### Feasibility-Aware Decision Policy

- [ ] Domain-neutral policy-evidence contract
- [ ] Public/private feasibility adapter boundary
- [ ] Admissibility and feasibility recognition
- [ ] Cost and resource translation
- [ ] Utility and marginal-value translation
- [ ] Formal Stop/Switch/Scale boundaries
- [ ] Iterative policy execution
- [ ] Boundary, transition, and replay testing
- [ ] Public evidence without private-theory disclosure

### Distributed HPC–Quantum Execution

- [ ] Distributed execution contracts
- [ ] Workload decomposition
- [ ] Backend scheduling
- [ ] Concurrent heterogeneous execution
- [ ] Result aggregation
- [ ] Partial-result handling
- [ ] Timeout, retry, and failure policies
- [ ] HPC resource and cost telemetry
- [ ] Distributed-method applicability assessment
- [ ] Distributed telemetry in policy decisions

### Research Validation and Evidence

- [ ] Experiment configuration and result schema
- [ ] Reproducible benchmark suite
- [ ] Determinism, idempotency, and seeded-execution validation
- [ ] Performance and evidence dashboard
- [ ] Portfolio, scientific, and hybrid demonstration notebooks
- [ ] Engineering evidence ledger
- [ ] Claims mapped to tests, artifacts, benchmarks, and releases
- [ ] Experimental reproducibility protocol
- [ ] Clean-install and release-artifact validation
- [ ] Licensing, security, privacy, and IP review

## GitHub Object Hierarchy

```text
docs/ROADMAP.md
    Big-picture direction, capability progress, release order, and concept
    mappings.

GitHub Milestone
    One planned software release, including purpose, scope, exclusions,
    dependencies, required issues, and release-level exit criteria.

Feature Issue
    One bounded capability that must ship in the milestone.

Sub-issue
    A separately trackable implementation, test, documentation, or research
    unit required by a feature.

Pull Request
    The reviewed change implementing or closing one or more issues.

Git tag
    A fixed reference to the exact released commit.

GitHub Release
    The published version associated with the tag, including release notes and
    downloadable assets. Published releases are treated as immutable; GitHub
    enforces immutability only when release immutability is enabled.

GitHub Project
    The live planning and execution view over canonical issues and their
    status, milestone, priority, effort, workstream, ownership, dates, and
    dependencies.

Architecture documents
    System structure, boundaries, responsibilities, and control/data flow.

Architecture Decision Records
    The rationale, alternatives, tradeoffs, and consequences for major design
    decisions.

Evidence ledger
    Verified claims mapped to tests, benchmarks, artifacts, source files, and
    released versions.
```