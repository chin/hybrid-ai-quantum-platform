# OptEngine Mermaid Architecture

> **Mathematical rendering:** Equations use LaTeX. Mermaid flowcharts use `$$...$$`; substantial equations are also stated as Markdown math in the diagram atlas.

> Compact visual companion to [the detailed architecture](./detailed-architecture.md).
>
> The diagrams describe the target object-collaboration architecture. Implementation sequencing is tracked in the [roadmap](./ROADMAP.md).

## 1. End-to-end control flow

```mermaid
flowchart TD
    INPUT[Raw input and configuration]
    ASSEMBLE[Construct Domain aggregate]
    INTERPRET[Domain.interpret]
    INTERPRETATION[Interpretation]
    OBJECTIVE[Objective]
    EXPRESSION[Expression]
    CURVE[Source Curve]

    FORMULATE{Each Formulation.express}
    REJECTED[Compatibility rejection evidence]
    MODEL[Model with payload decoder and target Curve]
    OPERATIONS[Compatible Operations]
    SOLVERS[Compatible Solvers]
    STRATEGIES[N immutable Strategies]

    EXECUTE[Execute each Strategy independently]
    PREPARE[Operation.prepare]
    SOLVE[Solver.execute]
    NATIVE[Native result or failure]
    DECODE[Model.decode]
    CANDIDATE[Domain Candidate]
    EVALUATE[Domain.interpret Candidate]
    DOMAIN_EVAL[Domain Evaluation]
    EXECUTION[Execution record]

    ASSESS[UtilityModel.assess]
    UTILITY[Utility]
    POLICY[Policy.apply]
    ACTION{Decision}

    STOP[Stop]
    SWITCH[Switch]
    SCALE[Scale]
    SELECT[Select another compatible Strategy]
    RESCALE[Create changed configuration budget or resources]

    EXPLAIN[Explainer]
    RECOMMEND[Recommendation]
    WRITE[Writer]
    OUTPUT[JSON outputs and curated artifacts]

    INPUT --> ASSEMBLE --> INTERPRET --> INTERPRETATION
    INTERPRETATION --> OBJECTIVE --> EXPRESSION --> CURVE --> FORMULATE
    FORMULATE -->|unsupported| REJECTED
    FORMULATE -->|compatible| MODEL
    MODEL --> OPERATIONS --> SOLVERS --> STRATEGIES

    STRATEGIES --> EXECUTE --> PREPARE --> SOLVE --> NATIVE
    NATIVE -->|success| DECODE --> CANDIDATE --> EVALUATE --> DOMAIN_EVAL --> EXECUTION
    NATIVE -->|failure| EXECUTION

    EXECUTION --> ASSESS --> UTILITY --> POLICY --> ACTION
    ACTION --> STOP
    ACTION --> SWITCH --> SELECT --> STRATEGIES
    ACTION --> SCALE --> RESCALE --> STRATEGIES
    STOP --> EXPLAIN --> RECOMMEND --> WRITE --> OUTPUT
```

## 2. Object collaboration map

```mermaid
flowchart LR
    subgraph DomainSemantics[Domain semantics]
        D[Domain]
        I[Interpretation]
        O[Objective]
        E[Expression]
        C[Curve]
        CAN[Candidate]
        DE[Domain Evaluation]

        D -->|interpret| I
        I --> O --> E --> C
        D -->|interpret candidate| DE
        CAN --> D
    end

    subgraph MathematicalPlugins[Mathematical plugins]
        F[Formulation]
        M[Model]
        TC[Target Curve]
        DEC[Decoder]

        F -->|express Objective| M
        M --> TC
        M --> DEC
    end

    subgraph ExecutionPlugins[Execution plugins]
        OP[Operation]
        S[Solver]
        NR[Native Result]

        M -->|filters| OP
        OP -->|filters| S
        OP -->|prepare| S
        S --> NR
    end

    subgraph EngineEvidence[Engine evidence and control]
        ST[Strategy]
        EX[Execution]
        UM[UtilityModel]
        U[Utility]
        P[Policy]
        PD[Policy Decision]
        R[Recommendation]

        M --> ST
        OP --> ST
        S --> ST
        ST --> EX
        DE --> EX
        EX --> UM --> U --> P --> PD --> R
    end

    O --> F
    NR --> DEC --> CAN
```

## 3. Core class responsibilities

```mermaid
classDiagram
    class Domain {
        <<abstract>>
        +interpret() Interpretation
        +interpret(candidate) Evaluation
        #_interpret_domain() Interpretation
        #_interpret_candidate(candidate) Evaluation
    }

    class Interpretation {
        +Objective objective
        +metadata
    }

    class Objective {
        +sense
        +Expression expression
        +curve Curve
    }

    class Expression {
        +Variable[] variables
        +LinearTerm[] linear_terms
        +QuadraticTerm[] quadratic_terms
        +Constraint[] constraints
        +constant
        +degree
        +curve Curve
    }

    class Curve {
        +input_types
        +input_count
        +output_types
        +output_count
        +degree
        +constraint_count
        +constraint_degrees
    }

    class Formulation {
        <<abstract>>
        +Capability capability
        +express(Objective) Model
    }

    class Model {
        +Objective objective
        +payload
        +source_curve
        +target_curve
        +decoder
        +metadata
        +fingerprint
        +operations(available)
        +decode(native_result) Candidate
    }

    class Operation {
        <<abstract>>
        +Capability capability
        +solvers(Model, available)
        +prepare(Model, configuration)
    }

    class Solver {
        <<abstract>>
        +Capability capability
        +available
        +execute(request)
    }

    class Strategy {
        +Formulation formulation
        +Model model
        +Operation operation
        +Solver solver
        +configuration
        +seed
        +budget
        +fingerprint
    }

    class Execution {
        +Strategy strategy
        +status
        +native_result
        +candidate
        +evaluation
        +runtime
        +failure
    }

    class UtilityModel {
        <<abstract>>
        +assess(Execution[]) Utility
    }

    class Utility {
        +Execution[] executions
        +scores
        +ranking
        +evidence
        +best
    }

    class Policy {
        <<abstract>>
        +apply(Utility) Decision
    }

    class Recommendation {
        +Domain domain
        +Analysis analysis
        +Execution[] executions
        +Utility utility
        +Decision decision
        +Explanation explanation
    }

    Domain --> Interpretation
    Interpretation --> Objective
    Objective --> Expression
    Expression --> Curve
    Objective --> Formulation
    Formulation --> Model
    Model --> Operation
    Operation --> Solver
    Formulation --> Strategy
    Model --> Strategy
    Operation --> Strategy
    Solver --> Strategy
    Strategy --> Execution
    Execution --> UtilityModel
    UtilityModel --> Utility
    Utility --> Policy
    Policy --> Recommendation
```

## 4. Strategy discovery sequence

```mermaid
sequenceDiagram
    participant Engine as OptEngine
    participant Analyzer
    participant Domain
    participant Catalog
    participant Formulation
    participant Model
    participant Operation
    participant Solver

    Engine->>Analyzer: analyze(domain, catalog)
    Analyzer->>Domain: interpret()
    Domain-->>Analyzer: Interpretation(Objective)
    Analyzer->>Catalog: formulations

    loop each Formulation
        Analyzer->>Formulation: express(Objective)
        alt source Curve supported
            Formulation-->>Analyzer: Model
            Analyzer->>Model: operations(catalog.operations)
            Model-->>Analyzer: compatible Operations
            loop each Operation
                Analyzer->>Operation: solvers(Model, catalog.solvers)
                Operation-->>Analyzer: compatible Solvers
                loop each Solver
                    Analyzer->>Analyzer: build unique Strategy fingerprint
                end
            end
        else unsupported
            Formulation-->>Analyzer: None
            Analyzer->>Analyzer: record rejection evidence
        end
    end

    Analyzer-->>Engine: Analysis with N Strategies
```

## 5. Failure-isolated execution sequence

```mermaid
sequenceDiagram
    participant Engine as OptEngine
    participant Strategy
    participant Operation
    participant Solver
    participant Model
    participant Domain
    participant UtilityModel
    participant Policy
    participant Explainer
    participant Writer

    loop each Strategy independently
        Engine->>Operation: prepare(Model, configuration)
        Operation-->>Engine: native request
        Engine->>Solver: execute(request)
        alt solver succeeds
            Solver-->>Engine: native result
            Engine->>Model: decode(native result)
            Model-->>Engine: Domain Candidate
            Engine->>Domain: interpret(candidate)
            Domain-->>Engine: Domain Evaluation
            Engine->>Engine: record complete Execution
        else solver fails
            Solver--xEngine: exception or failed result
            Engine->>Engine: record failed Execution
        end
    end

    Engine->>UtilityModel: assess(Execution[])
    UtilityModel-->>Engine: Utility
    Engine->>Policy: apply(Utility)
    Policy-->>Engine: Stop Switch or Scale
    Engine->>Explainer: explain structured evidence
    Explainer-->>Engine: Explanation
    Engine->>Writer: write(Recommendation)
```

## 6. Domain polymorphism

```mermaid
flowchart TD
    ENGINE[Domain-neutral OptEngine]
    DOMAIN[Domain contract]
    MAXCUT[MaxCut aggregate]
    PORTFOLIO[Portfolio aggregate]
    FUTURE[Future scientific or logistics domain]

    ENGINE --> DOMAIN
    MAXCUT -->|implements interpret overload| DOMAIN
    PORTFOLIO -->|implements interpret overload| DOMAIN
    FUTURE -->|implements interpret overload| DOMAIN

    MAXCUT --> MAXOBJ[Binary quadratic cut Objective]
    PORTFOLIO --> PORTOBJ[Constrained risk-return Objective]
    FUTURE --> FUTOBJ[Domain-specific Objective]

    MAXOBJ --> PLUGINS[Shared Formulation Operation Solver catalog]
    PORTOBJ --> PLUGINS
    FUTOBJ --> PLUGINS

    PLUGINS --> SHARED[Shared Analysis Execution Utility Policy Recommendation]
```

## 7. Max-Cut reference path

```mermaid
flowchart LR
    MC[MaxCut aggregate]
    MCI[MaxCut.interpret]
    OBJ[Maximize Objective]
    EXP[Binary quadratic Expression]
    CURVE[Unconstrained binary quadratic Curve]
    QUBO[QUBO.express]
    MODEL[QUBO Model]

    EXACT[ExactSearch]
    ANNEAL[Annealing]
    DIMOD[DimodExact]
    DWAVE[DWaveLocal]

    SAMPLE[Native sample]
    DECODE[Model.decode]
    CAND[MaxCut Candidate]
    EVAL[MaxCut.interpret Candidate]
    EVIDENCE[Cut value partitions crossing edges feasibility]

    MC --> MCI --> OBJ --> EXP --> CURVE --> QUBO --> MODEL
    MODEL --> EXACT --> DIMOD --> SAMPLE
    MODEL --> ANNEAL --> DWAVE --> SAMPLE
    SAMPLE --> DECODE --> CAND --> EVAL --> EVIDENCE
```

## 8. Portfolio acceptance and Vanguard extension

```mermaid
flowchart LR
    P[Portfolio aggregate]
    PI[Portfolio.interpret]
    PO[Constrained quadratic Objective]
    PC[Source Curve]

    CONT[Continuous constrained Formulation]
    CQM[CQM Formulation]
    PQ[Penalty-QUBO Formulation]

    CM[Continuous Model]
    CQMM[CQM Model]
    QM[Unconstrained QUBO Model]

    CS[Classical continuous Solver]
    CE[Classical exact or heuristic Solver]
    QS[Annealing or QAOA Solver]

    CAND[Portfolio Candidate]
    EVAL[Portfolio Evaluation]

    P --> PI --> PO --> PC
    PC --> CONT --> CM --> CS --> CAND
    PC --> CQM --> CQMM --> CE --> CAND
    PC --> PQ --> QM --> QS --> CAND
    CAND --> EVAL
```

## 9. Stop, Switch, and Scale loops

```mermaid
stateDiagram-v2
    [*] --> Analyze
    Analyze --> Execute: compatible Strategies exist
    Analyze --> ExplainFailure: no compatible Strategy

    Execute --> Assess
    Assess --> Decide

    Decide --> Stop: sufficient utility or terminal condition
    Decide --> Switch: another Strategy is preferable
    Decide --> Scale: more resources remain justified

    Switch --> Execute: select existing Strategy
    Switch --> Analyze: eligibility or formulation changes
    Scale --> Execute: new configuration fingerprint

    Stop --> Explain
    ExplainFailure --> Recommend
    Explain --> Recommend
    Recommend --> Write
    Write --> [*]
```

## 10. Branch-by-abstraction migration

```mermaid
flowchart TD
    BASELINE[Freeze tests CLI JSON artifacts and public imports]
    CONTRACTS[Add new contracts alongside old contracts]
    SHIMS[Add temporary compatibility aliases]
    MAXCUT[Port Max-Cut reference path]
    ANALYSIS[Replace Analysis internals]
    EXECUTION[Replace Execution and Utility internals]
    PORTFOLIO[Port Portfolio without engine branches]
    RELEASE[Publish release boundary]
    REMOVE[Remove temporary shims]

    BASELINE --> CONTRACTS --> SHIMS --> MAXCUT --> ANALYSIS --> EXECUTION --> PORTFOLIO --> RELEASE --> REMOVE
```

## 11. Logical dependency direction

```mermaid
flowchart BT
    ENGINE[engine orchestration]
    RECOMMEND[recommendation explanation writer]
    POLICY[utility and policy]
    EXEC[analysis strategy execution]
    PLUGINS[formulations operations solvers]
    MATH[objective expression curve]
    DOMAINS[domain aggregates]

    ENGINE --> RECOMMEND
    ENGINE --> POLICY
    ENGINE --> EXEC
    EXEC --> PLUGINS
    PLUGINS --> MATH
    DOMAINS --> MATH
    EXEC --> DOMAINS

    MAXRULE[Core engine must not import concrete domains]
    MAXRULE -. constrains .-> ENGINE
```

## 12. Interpretation overload contract

```mermaid
flowchart TD
    CALL{Call form}
    OMITTED[domain.interpret with argument omitted]
    NONE[domain.interpret with explicit None]
    CAND[domain.interpret with Candidate]

    DOMAINHOOK[_interpret_domain]
    CANDHOOK[_interpret_candidate]
    INVALID[Candidate validation failure or infeasible evaluation]
    INTERP[Interpretation]
    EVAL[Evaluation]

    CALL --> OMITTED --> DOMAINHOOK --> INTERP
    CALL --> NONE --> CANDHOOK --> INVALID
    CALL --> CAND --> CANDHOOK --> EVAL
```

The implementation uses `typing.overload` plus a private sentinel. `None` must never serve as the omission sentinel when the two call forms have different semantics.


## Detailed diagram atlas

See the [Mermaid + LaTeX diagram atlas](./diagrams/README.md).
