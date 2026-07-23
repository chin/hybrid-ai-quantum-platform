# OptEngine Detailed Architecture

> **Mathematical rendering:** Mathematical variables and equations in this document use GitHub-compatible LaTeX. Inline notation uses `$...$`; display equations use `$$...$$`. Mermaid flowcharts use embedded `$$...$$` math syntax.

> Target collaboration architecture for the branch-by-abstraction refactor.
>
> This document defines object ownership, handoffs, invariants, and migration rules. It does not claim that every target component is already implemented.

Related documents:

- [Compact Mermaid architecture](./mermaid-architecture.md)
- [Development roadmap](./ROADMAP.md)

## 1. Architectural objective

OptEngine is a domain-neutral orchestration engine. A concrete domain supplies meaning; mathematical and execution plugins supply compatible transformations and operations; the engine coordinates the workflow without inspecting domain-specific classes.

The canonical collaboration is:

```text
Domain
→ Interpretation
→ Objective
→ Expression
→ Curve
→ Formulation.express(Objective)
→ Model
→ Operation
→ Solver
→ native result
→ Model.decode(native result)
→ Domain Candidate
→ Domain.interpret(Candidate)
→ Domain Evaluation
→ Execution
→ UtilityModel.assess(Execution[])
→ Utility
→ Policy.apply(Utility)
→ Stop | Switch | Scale
→ Explanation
→ Recommendation
→ Writer
```

The central rule is:

> The engine owns the workflow pattern. Collaborating objects own the behavior specific to their responsibility.

## 2. Core architectural principles

### 2.1 Domain owns semantic interpretation

A domain defines what its entities, relationships, objectives, candidates, and evaluations mean.

```python
interpretation = domain.interpret()
evaluation = domain.interpret(candidate)
```

Examples:

- `MaxCut.interpret()` produces a cut-maximization objective.
- `MaxCut.interpret(candidate)` interprets a partition as crossing edges, cut weight, and feasibility.
- `Portfolio.interpret()` produces a risk/return/cost objective with constraints.
- `Portfolio.interpret(candidate)` interprets allocations as return, risk, costs, violations, and feasibility.

The engine must not contain branches such as:

```python
if isinstance(domain, MaxCut):
    ...
elif isinstance(domain, Portfolio):
    ...
```

### 2.2 Formulation owns mathematical expression into a model

The domain does not directly encode itself for QUBO, CQM, Hamiltonian, or another backend-oriented representation.

```python
model = formulation.express(objective)
```

A formulation:

- checks whether it can express the objective's mathematical structure;
- constructs a solver-oriented `Model`;
- records any transformation assumptions;
- supplies the decoder that maps native results back to a domain candidate.

### 2.3 Model owns the encoded payload and decoding

A `Model` is the immutable result of formulation.

It owns:

- the source `Objective`;
- the formulated payload;
- the target mathematical profile;
- the decoder;
- transformation metadata;
- a stable fingerprint.

```python
candidate = model.decode(native_result)
```

The model understands the encoded/native representation. The domain understands the decoded candidate's meaning.

### 2.4 Operation owns preparation; Solver owns execution

An `Operation` describes what kind of computation will be applied to a model, such as exact search, annealing, or QAOA.

A `Solver` performs the native execution for a supported operation/model combination.

```python
request = operation.prepare(model, configuration)
native_result = solver.execute(request)
```

### 2.5 Analysis produces immutable Strategies

A `Strategy` is the explicit output of compatible object collaboration:

```text
Formulation + Model + Operation + Solver + Configuration
```

It preserves:

- provenance;
- requested-strategy filtering;
- deterministic identity;
- execution configuration;
- deduplication;
- replay and idempotency controls.

### 2.6 Evaluation and utility are different

A domain evaluation answers:

> What does this candidate mean in this domain?

Utility answers:

> How valuable is this complete execution compared with other executions?

Utility can depend on more than domain quality:

- feasibility;
- runtime;
- resource cost;
- uncertainty;
- solver availability;
- failure state;
- strategy provenance.

### 2.7 Policy owns Stop, Switch, and Scale

The domain does not issue the final control action. The policy consumes `Utility` and returns a decision with evidence.

- **Stop:** finalize the current recommendation.
- **Switch:** select an alternative compatible strategy or workflow.
- **Scale:** change budget, precision, sampling, resources, or another declared configuration and execute again.

### 2.8 External behavior is versioned separately from internal refactoring

Internal class renames or ownership changes must not silently rename public JSON fields, CLI sections, Make targets, artifact paths, or public imports.

Schema changes require an explicit versioned migration.

## 3. Canonical stage workflow

```text
INPUT
    ↓
Construct Domain aggregate
    ↓

ANALYZE
    ↓
Domain.interpret()
    ↓
Interpretation
    ↓
Objective
    ↓
Expression
    ↓
Curve
    ↓
Each Formulation.express(Objective)
    ↓
Zero or one Model per Formulation
    ↓
Each Model filters compatible Operations
    ↓
Each Operation filters compatible Solvers
    ↓
N immutable Strategies
    ↓

EXECUTE / EVALUATE
    ↓
Each Strategy executes independently
    ↓
Operation.prepare(Model, configuration)
    ↓
Solver.execute(request)
    ↓
Native result
    ↓
Model.decode(native result)
    ↓
Domain Candidate
    ↓
Domain.interpret(Candidate)
    ↓
Domain Evaluation
    ↓
Immutable Execution record
    ↓

DECIDE
    ↓
Execution[]
    ↓
UtilityModel.assess(Execution[])
    ↓
Utility
    ↓
Policy.apply(Utility)
    ↓
Stop | Switch | Scale
    ↓

EXPLAIN
    ↓
Explanation grounded in Analysis, Executions, Utility, and Decision
    ↓

WRITE
    ↓
Recommendation
    ↓
JSON, disposable outputs, and curated artifacts
```

The public CLI may retain its established section names during migration even if internal class names change.

## 4. Object responsibility map

| Object | Primary responsibility | Must not own |
|---|---|---|
| `Domain` | Entities, relationships, semantic interpretation, candidate evaluation | Backend selection, solver execution, policy action |
| `Interpretation` | Immutable result of interpreting a domain aggregate | Native solver payload |
| `Objective` | Optimization sense and source expression | Backend-specific encoding |
| `Expression` | Variables, terms, constraints, constant | Solver compatibility decisions |
| `Curve` | Normalized structural mathematical profile | Named domain identity or runtime results |
| `Formulation` | Express an objective as a compatible model | Execute a solver or evaluate a candidate |
| `Model` | Formulated payload, target curve, decoder, metadata | Domain evaluation or policy |
| `Operation` | Prepare a model for a class of execution | Native backend implementation |
| `Solver` | Execute a prepared native request | Domain semantics or final utility |
| `Catalog` | Available formulations, operations, and solvers | Hard-coded compatibility branches |
| `Analyzer` | Discover compatible strategies | Execute strategies |
| `Strategy` | Immutable executable collaboration and identity | Mutable runtime state |
| `Execution` | Immutable success/failure evidence for one strategy | Comparative utility calculation |
| `UtilityModel` | Behavior for comparative assessment | Persistence of the result |
| `Utility` | Immutable comparative result and ranking | Policy behavior |
| `Policy` | Stop/Switch/Scale action based on utility | Domain-specific objective calculation |
| `Explainer` | Human-readable, evidence-grounded explanation | Invented results or solver grading |
| `Recommendation` | Complete engine result | File-system side effects |
| `Writer` | Serialization and persistence | Recomputing domain or utility values |

## 5. Domain aggregate and interpretation

### 5.1 Aggregate construction

A domain aggregate contains domain entities and their relationships.

A generic input assembler should construct relational domains in two passes:

```text
1. Construct entities.
2. Resolve relationships using object references.
3. Construct and validate the Domain aggregate.
```

Examples:

```python
MaxCut.Edge(
    first=vertex_a,
    second=vertex_b,
    weight=1.0,
)
```

```python
Portfolio.Covariance(
    first_asset=growth,
    second_asset=income,
    value=0.006,
)
```

Relationships should hold object references rather than duplicate string identifiers wherever practical.

### 5.2 One public interpretation behavior with two valid calls

The public contract intentionally supports:

```python
domain.interpret()
domain.interpret(candidate)
```

Python implements the Java-like overloaded call surface through `typing.overload`, one runtime method, and a private omission sentinel.

```python
from typing import overload

_MISSING = object()

class Domain:
    @overload
    def interpret(self) -> Interpretation:
        ...

    @overload
    def interpret(self, candidate: Candidate) -> Evaluation:
        ...

    def interpret(
        self,
        candidate: Candidate | object = _MISSING,
    ) -> Interpretation | Evaluation:
        if candidate is _MISSING:
            return self._interpret_domain()

        return self._interpret_candidate(candidate)
```

The protected hooks remain domain-specific:

```python
def _interpret_domain(self) -> Interpretation:
    ...

def _interpret_candidate(self, candidate: Candidate) -> Evaluation:
    ...
```

### 5.3 Omission is not `None`

These calls are semantically different:

```python
domain.interpret()
domain.interpret(None)
```

- Omission invokes aggregate interpretation.
- Explicit `None` is a supplied candidate and must follow candidate validation.

The codebase-wide overload convention is:

1. declare every supported signature with `@overload`;
2. provide one concrete runtime implementation;
3. use a private sentinel whenever omission differs from `None`;
4. avoid broad `*args`/`**kwargs` dispatch;
5. reject unsupported combinations explicitly.

## 6. Mathematical objects

### 6.1 `Variable`

A variable declares:

- stable name;
- value type;
- optional lower and upper bounds.

Initial value types include:

```text
binary
integer
real
categorical
```

Future scientific workflows may extend the type system with structured tensors, fields, or sequences through explicit contracts rather than overloading the existing scalar meanings.

### 6.2 `Expression`

An expression contains:

- variables;
- linear terms;
- quadratic terms;
- constraints;
- constant term.

The MVP supports scalar polynomial objectives up to degree two. Higher-order or non-polynomial forms are rejected unless a formulation explicitly supports or transforms them.

### 6.3 `Objective`

An objective contains:

```text
sense: maximize | minimize
expression: Expression
```

The first implementation uses one scalar objective. Multi-objective behavior is represented by a declared scalarization or a later composite-objective extension, not by hidden solver-specific weighting.

### 6.4 `Curve`

`Curve` is the normalized structural mathematical profile used for compatibility.

It records properties such as:

- input value types and counts;
- output value types and counts;
- expression degree;
- constraint count and degrees;
- bounds or other declared structural requirements.

`Curve` does not identify a named domain such as Max-Cut or Portfolio.

It is also not the dissertation's resilience trajectory. It is a software compatibility profile of a mathematical expression or model.

Example source curves:

```text
Max-Cut
    binary inputs $\times \lvert V\rvert$
    one real output
    degree 2
    no explicit constraints
```

```text
Bounded portfolio
    integer or binary inputs $\times N$
    one real output
    degree 2
    budget, bounds, and optional cardinality constraints
```

## 7. Formulation and Model collaboration

### 7.1 Capability-driven formulation

A formulation determines compatibility from the objective's source curve rather than a domain name.

```python
model = formulation.express(objective)
```

Return behavior:

- `Model` when the formulation can safely express the objective;
- `None` when the actual source curve is unsupported.

A formulation capability may constrain:

- supported input types;
- maximum degree;
- maximum inputs and outputs;
- constraint support;
- maximum constraint degree.

### 7.2 Source curve and target curve

A formulation can preserve or transform mathematical structure.

Examples:

- Max-Cut objective → unconstrained QUBO: mostly structure-preserving.
- Constrained Portfolio objective → penalty QUBO: constraints become objective penalties.
- Constrained Portfolio objective → CQM: constraints remain explicit.

Therefore a `Model` must preserve both concepts:

```text
source_curve
    Structural profile of the Domain Objective.

target_curve
    Structural profile of the formulated payload consumed by Operations and Solvers.
```

For structure-preserving formulations they may be equal. For structure-changing formulations they must differ, and transformation metadata must explain why.

Operations and solvers evaluate the **target curve**, not the pre-formulation source curve.

### 7.3 Model invariants

A model is immutable and contains:

- formulation identity;
- source objective;
- payload;
- source curve;
- target curve;
- decoder;
- transformation metadata;
- stable model fingerprint.

The decoder performs:

```text
native solver result → domain Candidate
```

It must not perform domain evaluation.

## 8. Operation and Solver collaboration

### 8.1 Operation

An operation expresses how a compatible model is acted upon.

Examples:

```text
ExactSearch
Annealing
QAOA
ContinuousOptimization
SurrogateInference
```

An operation:

- declares a nested capability;
- filters models by target curve;
- prepares a native request from a model and configuration;
- does not instantiate or select concrete solvers.

### 8.2 Solver

A solver is a concrete executor.

Examples:

```text
DimodExact
DWaveLocal
CudaQSimulator
ScipyOptimizer
PhysicsNeMoRuntime
```

A solver:

- declares supported operation types;
- declares target value types and size limits;
- exposes availability;
- executes a prepared request;
- returns a native result or raises a captured failure.

A solver does not know how to interpret a domain candidate.

### 8.3 Open/closed plugin filtering

Models and operations filter an injected catalog polymorphically:

```python
operations = model.operations(catalog.operations)
solvers = operation.solvers(model, catalog.solvers)
```

They must not hard-code or instantiate concrete plugin classes.

## 9. Catalog, Analysis, and Strategy

### 9.1 Catalog

A catalog contains available plugin instances:

```text
Formulation[]
Operation[]
Solver[]
```

Future registries may build the catalog through entry points, configuration, or dependency injection, but analysis consumes one stable catalog contract.

### 9.2 Analyzer

The analyzer:

1. obtains `domain.interpret()`;
2. extracts the objective;
3. asks every formulation to express it;
4. asks each model for compatible operations;
5. asks each operation for compatible solvers;
6. constructs unique immutable strategies;
7. applies requested-strategy, budget, and availability filters;
8. records compatibility and rejection evidence.

There is no domain-specific analyzer branch.

### 9.3 Strategy

A strategy contains:

```text
Formulation
Model
Operation
Solver
Configuration
Seed
Budget
```

Its stable execution fingerprint should include:

```text
model fingerprint
+ operation identity
+ solver identity
+ normalized configuration
+ seed
+ budget
```

The fingerprint supports:

- deterministic deduplication;
- provenance;
- replay;
- cache lookup;
- idempotency keys for remote or costly execution.

## 10. Execution and failure isolation

Every strategy executes independently.

```text
Strategy
→ Operation.prepare(Model, configuration)
→ Solver.execute(request)
→ native result
→ Model.decode(native result)
→ Candidate
→ Domain.interpret(Candidate)
→ Evaluation
→ Execution
```

An immutable `Execution` records:

- strategy;
- status;
- native result when retained safely;
- candidate;
- domain evaluation;
- runtime;
- resource evidence;
- failure details;
- timestamps and provenance.

A failed solver must produce an explicit failed execution rather than terminate the entire run.

```text
one Strategy fails
→ failed Execution is retained
→ other Strategies continue
→ UtilityModel handles the failure according to declared rules
→ Recommendation can still be produced
```

## 11. Utility and policy

### 11.1 UtilityModel

`UtilityModel` is behavior:

```python
utility = utility_model.assess(executions)
```

It compares complete executions, not only domain evaluations.

Swappable implementations can include:

```text
OperationalUtilityModel
OptChinUtilityAdapter
```

Both produce the same `Utility` contract.

### 11.2 Utility

`Utility` is an immutable result containing:

- the assessed executions;
- scores keyed by strategy fingerprint;
- ranking;
- evidence;
- best successful execution when one exists;
- dominance relationships when defined.

### 11.3 Policy

The policy consumes `Utility` and emits an immutable decision:

```text
action
reason code
supporting evidence
human-readable rationale
next strategy, when switching
resource change, when scaling
```

Solver identity alone must never determine the action.

### 11.4 Control-loop behavior

- `Stop` proceeds to explanation and recommendation.
- `Switch` selects another existing strategy or re-analyzes under changed eligibility criteria.
- `Scale` derives a new configuration/budget and executes a new strategy fingerprint.

Every loop iteration must remain bounded and observable.

## 12. Explanation, Recommendation, and Writer

### 12.1 Explainer

The explainer receives structured evidence:

```text
Domain
Analysis
Execution[]
Utility
Decision
```

It does not invent metrics or replace deterministic evaluation.

### 12.2 Recommendation

`Recommendation` is the top-level immutable engine result.

It contains:

- domain identity and safe domain summary;
- analysis and discovered strategies;
- executions, including failures;
- utility;
- policy decision;
- explanation;
- artifact references and provenance.

### 12.3 Writer

The writer serializes and persists a recommendation.

It must:

- preserve current external keys during the internal refactor;
- record schema and software versions;
- separate disposable outputs from curated artifacts;
- avoid recomputing objective, evaluation, utility, or policy values;
- retain enough configuration to reproduce equivalent evidence;
- promote artifacts non-destructively.

## 13. Max-Cut reference collaboration

Max-Cut is the first migration and compatibility proving ground.

### 13.1 Aggregate

```text
MaxCut
├── Vertex[]
└── Edge[]
    ├── first: Vertex
    ├── second: Vertex
    └── weight: float
```

### 13.2 Domain interpretation

For each vertex, Max-Cut produces a binary variable.

For each weighted edge $(u,v)$, the edge contribution is:

$$
w_{uv}\left(x_u+x_v-2x_u x_v\right).
$$

The objective is to maximize total crossing-edge weight:

$$
C(x)=\sum_{(u,v)\in E} w_{uv}\left(x_u+x_v-2x_u x_v\right).
$$

```text
MaxCut.interpret()
→ Interpretation
→ Objective(maximize)
→ quadratic binary Expression
→ unconstrained binary quadratic Curve
```

### 13.3 Strategy discovery

A QUBO formulation can express the objective.

Compatible collaborations may include:

```text
QUBO + ExactSearch + DimodExact
QUBO + Annealing + DWaveLocal
QUBO + QAOA + CudaQSimulator
```

Only available and capability-compatible combinations become strategies.

### 13.4 Candidate interpretation

```text
native sample
→ Model.decode(...)
→ MaxCut.Candidate(assignments)
→ MaxCut.interpret(candidate)
→ MaxCut.Evaluation
```

Evaluation records:

- complete binary assignment;
- partition membership;
- crossing edges;
- cut value;
- feasibility;
- domain evidence.

### 13.5 Migration acceptance

The old and new Max-Cut paths must use identical fixtures and produce equivalent domain outputs.

For nondeterministic operations compare invariants:

- all vertices are assigned;
- assignments are binary;
- cut value is independently recomputed;
- feasibility is equivalent;
- strategy provenance is present;
- seeded runs are reproducible where supported.

## 14. Portfolio extension collaboration

Portfolio is the architectural acceptance test that proves a second domain can use the collaboration model without engine changes.

### 14.1 Aggregate

A bounded portfolio domain may contain:

```text
Portfolio
├── Asset[]
├── ExpectedReturn[]
├── Covariance[]
├── CurrentAllocation[]
├── Constraint[]
└── preference parameters
```

### 14.2 Domain interpretation

```text
Portfolio.interpret()
→ Objective
→ quadratic constrained Expression
→ constrained integer/real Curve
```

The objective may combine:

- expected return reward;
- covariance risk penalty;
- transaction-cost penalty;
- concentration penalty.

A representative utility is:

$$
U(w)=\mu^\top w-\lambda w^\top\Sigma w-C_{\mathrm{tx}}(w,w^{(0)})-C_{\mathrm{conc}}(w).
$$

Constraints may include:

- full budget;
- bounds;
- cardinality;
- liquidity;
- exposure limits.

### 14.3 Formulation choices

The same source objective may be expressed through different formulations:

```text
Continuous constrained formulation
CQM formulation
Penalty-QUBO formulation
```

A penalty-QUBO formulation must expose an unconstrained target curve and record:

- penalty weights;
- scaling;
- variable encoding;
- transformation assumptions;
- decoder metadata.

### 14.4 Acceptance rule

Adding Portfolio must add domain objects and compatible plugins, not Portfolio branches inside `OptEngine`, `Analyzer`, `UtilityModel`, or `Policy`.

## 15. Determinism, idempotency, and provenance

Pure transformations should be deterministic and idempotent for equivalent inputs:

```text
domain.interpret()
objective.expression.curve
formulation.express(objective)
model.decode(native result)
domain.interpret(candidate)
analyzer.analyze(domain, catalog)
utility_model.assess(executions)
writer serialization
```

`Solver.execute()` is not inherently idempotent because it may:

- use randomness;
- consume remote resources;
- submit a QPU job;
- incur cost;
- return time-sensitive metadata.

Use strategy execution fingerprints as idempotency keys where supported.

Every recommendation should retain:

- domain and input identity;
- model/formulation identity;
- operation and solver identity;
- configuration, seed, and budget;
- software version;
- timestamps;
- candidate and evaluation;
- utility and decision evidence;
- failures and negative results;
- artifact references.

## 16. Error and unsupported-state behavior

Unsupported behavior must be explicit.

- Unsupported formulation: `express()` returns `None` with compatibility evidence recorded by analysis.
- Invalid domain aggregate: construction or interpretation fails before strategy creation.
- Invalid candidate: candidate interpretation returns an explicit infeasible evaluation or raises a typed validation failure according to the domain contract.
- Unavailable solver: filtered from executable strategies or represented as an explicit unavailable status.
- Solver failure: retained as a failed execution.
- No compatible strategy: analysis returns zero strategies and the engine produces a structured failure recommendation.
- No successful execution: utility and policy follow declared fallback behavior without fabricating a result.

## 17. Logical module boundaries

The precise package layout may evolve, but dependencies should follow these logical boundaries:

```text
optengine/
├── domains/
│   ├── base
│   ├── maxcut
│   └── portfolio
├── mathematics/
│   ├── objective
│   ├── expression
│   ├── curve
│   └── variable
├── formulations/
│   ├── base
│   ├── qubo
│   ├── cqm
│   └── continuous
├── operations/
│   ├── base
│   ├── exact
│   ├── annealing
│   └── qaoa
├── solvers/
│   ├── base
│   └── adapters
├── analysis/
│   ├── catalog
│   ├── analyzer
│   └── strategy
├── execution/
│   └── execution
├── utility/
│   ├── model
│   └── utility
├── policy/
├── explanation/
├── recommendation/
├── artifacts/
└── engine/
```

Core engine modules must not import concrete domain modules.

## 18. Branch-by-abstraction migration

The refactor must proceed alongside the current implementation.

### Step 1 — Freeze observable behavior

Capture:

```text
test count and pass status
coverage
CLI section order
Max-Cut exact output
Max-Cut annealing invariants
current Portfolio output
Recommendation JSON
artifact paths
public imports
failure behavior
```

Normalize timestamps, UUIDs, runtimes, and temporary paths in snapshots.

### Step 2 — Add target contracts alongside current contracts

Add:

```text
Domain interpretation overload
Objective
Expression
Curve
Formulation.express()
Model
Operation.Capability
Solver.Capability
Strategy fingerprint
Execution
Utility
Recommendation
```

Do not delete old interfaces yet.

### Step 3 — Add temporary compatibility shims

Examples:

```text
formulate() → express()
FormulationResult → Model
UtilityAssessment → Utility
ObjectiveShape → Curve
QUBOFormulation → QUBO
CQMFormulation → CQM
```

These are migration controls, not permanent architecture.

### Step 4 — Port Max-Cut completely

Use Max-Cut to prove:

- domain interpretation;
- curve-driven compatibility;
- formulation/model decoding;
- multiple strategies;
- independent executions;
- utility and policy;
- recommendation writing;
- regression equivalence.

### Step 5 — Replace Analysis and Execution internals

Preserve:

- requested-strategy filtering;
- N-strategy generation;
- deterministic ordering;
- deduplication;
- budget propagation;
- plugin discovery;
- failure isolation;
- native result retention;
- provenance.

### Step 6 — Port Portfolio without engine changes

Portfolio must reuse the same analyzer, execution, utility, policy, explanation, recommendation, and writer contracts.

### Step 7 — Preserve external behavior

Do not combine internal refactoring with an artifact-schema migration.

### Step 8 — Remove shims after a release boundary

Remove aliases only after:

- internal imports use the target names;
- demos use the target names;
- documentation uses the target names;
- public API tests use the target names;
- a release boundary is established.

## 19. Required verification layers

### Characterization tests

- Max-Cut exact output;
- Max-Cut annealing invariants;
- Portfolio output;
- CLI rendering;
- Recommendation JSON;
- artifact output.

### Contract tests

Every concrete implementation must satisfy its base contract.

### Compatibility tests

Verify expected matches and rejections for:

- binary quadratic unconstrained;
- binary quadratic constrained;
- integer quadratic constrained;
- real quadratic constrained;
- unsupported higher-order expressions;
- unsupported variable counts;
- unavailable solvers.

### Polymorphism tests

The engine must run Max-Cut and Portfolio without importing or inspecting either concrete domain class.

### Failure-isolation tests

- one solver fails;
- other strategies execute;
- failed execution is retained;
- utility handles failure according to policy;
- recommendation is still produced.

### Public API tests

Stable imports and compatibility aliases remain tested until their documented removal.

### Overload tests

For every intentional overloaded method:

- every declared call form works;
- omission and explicit `None` remain distinct;
- unsupported combinations fail explicitly;
- subclasses preserve the public contract.

## 20. Non-goals for the current MVP refactor

The object-collaboration refactor does not require:

- FNO implementation;
- PINN or QAPINN implementation;
- distributed execution;
- production QPU access;
- AI-controlled solver correctness;
- a learned Stop/Switch/Scale policy;
- a dashboard;
- a breaking public artifact-schema change;
- publication of private dissertation derivations.

The immediate goal is a stable collaboration pattern exercised first by Max-Cut and then proven domain-neutral by Portfolio.


## Diagram atlas

See the [Mermaid + LaTeX diagram atlas](./diagrams/README.md).
