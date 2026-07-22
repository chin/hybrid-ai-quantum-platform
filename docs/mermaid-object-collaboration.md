# OptEngine Mature Object-Collaboration — Mermaid Source

[Back to package index](./README.md)

These diagrams are editable Mermaid companions to the full rendered diagram set in [`DIAGRAMS.md`](./DIAGRAMS.md).

## 1. Generic domain overload and interpretation behavior

```mermaid
flowchart LR
    A[domain.interpret<br/>argument omitted]
    B[domain.interpret candidate<br/>argument supplied]
    N[domain.interpret None<br/>explicit value supplied]
    D{One runtime method<br/>_MISSING sentinel}
    H0[_interpret_domain]
    H1[_interpret_candidate]
    I[Interpretation<br/>Objective and metadata]
    E[Domain Evaluation<br/>quality feasibility evidence]

    A -->|candidate is _MISSING| D
    B -->|candidate supplied| D
    N -->|candidate supplied as None| D
    D -->|omitted| H0 --> I
    D -->|supplied| H1 --> E
```

## 2. Max-Cut aggregate self-interpretation

```mermaid
flowchart LR
    subgraph AGG[MaxCut aggregate]
        MC[MaxCut]
        V[Vertex array]
        ED[Edge array<br/>first Vertex<br/>second Vertex<br/>weight]
        MC --> V
        MC --> ED
    end

    subgraph SELF[max_cut.interpret]
        VAR[Binary variable x_v per Vertex]
        EX[Expression<br/>sum w_uv times x_u plus x_v minus 2 x_u x_v]
        OBJ[Objective<br/>maximize cut weight]
        CURVE[Curve<br/>binary<br/>degree 2<br/>unconstrained]
        VAR --> EX --> OBJ --> CURVE
    end

    subgraph CAND[max_cut.interpret candidate]
        CA[MaxCut Candidate<br/>Vertex to 0 or 1]
        CHECK[Validate complete binary assignment]
        CROSS[Identify crossing edges]
        EV[MaxCut Evaluation<br/>cut value ratio feasibility evidence]
        CA --> CHECK --> CROSS --> EV
    end

    MC -->|interpret self| VAR
    ED -. contributes terms .-> EX
    MC -. defines candidate meaning .-> CA
```

## 3. Portfolio aggregate self-interpretation

```mermaid
flowchart LR
    subgraph AGG[Portfolio aggregate]
        P[Portfolio]
        A[Asset array]
        C[Covariance array<br/>object references]
        G[Guardrails<br/>budget exposure liquidity cardinality]
        H[Current holdings]
        P --> A
        P --> C
        P --> G
        P --> H
    end

    subgraph SELF[portfolio.interpret]
        VAR[Allocation variables<br/>real weights or integer units]
        EX[Expression<br/>return minus risk minus costs minus concentration]
        CON[Constraints<br/>budget bounds exposure liquidity cardinality]
        OBJ[Objective<br/>maximize expected utility]
        CURVE[Curve<br/>real integer binary<br/>degree at most 2<br/>constrained]
        VAR --> EX --> OBJ --> CURVE
        CON --> EX
    end

    subgraph CAND[portfolio.interpret candidate]
        CA[Portfolio Candidate<br/>allocation by Asset]
        CHECK[Validate allocation and guardrails]
        MET[Compute return risk turnover concentration violations]
        EV[Portfolio Evaluation<br/>objective terms feasibility evidence]
        CA --> CHECK --> MET --> EV
    end

    P -->|interpret self| VAR
    C -. risk terms .-> EX
    G -. constraints .-> CON
    P -. defines candidate meaning .-> CA
```

## 4. Objective, Expression, and Curve

```mermaid
classDiagram
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
        +bounds_and_metadata
    }

    class Variable {
        +name
        +value_type
        +lower_bound
        +upper_bound
    }

    class Constraint {
        +name
        +relation
        +bound
        +degree
    }

    Objective *-- Expression
    Expression *-- Variable
    Expression *-- Constraint
    Expression --> Curve : derives
```

## 5. Formulation collaboration

```mermaid
flowchart LR
    O[Objective and source Curve]
    FC[Formulation catalog]
    CAP{Formulation Capability<br/>supports source Curve?}
    REJ[Compatibility rejection evidence]
    EXP[Formulation.express Objective]
    M[Immutable Model<br/>payload decoder<br/>source Curve target Curve<br/>metadata fingerprint]
    OPS[Model filters compatible Operations]

    O --> CAP
    FC --> CAP
    CAP -->|no| REJ
    CAP -->|yes| EXP --> M --> OPS
```

## 6. Formulation families

```mermaid
flowchart LR
    O[Objective and source Curve]

    O --> DQ[Direct QUBO]
    O --> PQ[Penalty QUBO<br/>validated penalties and discretization]
    O --> CQM[CQM or quadratic program]
    O --> H[Hamiltonian or Ising]

    DQ --> QB[Binary quadratic unconstrained Model]
    PQ --> QB
    CQM --> CM[Constrained binary integer or real Model]
    H --> HM[Qubit cost Hamiltonian Model]

    QB --> X[ExactSearch]
    QB --> A[Annealing]
    CM --> CO[ContinuousOptimization]
    CM --> CX[Bounded constrained exact or hybrid]
    HM --> Q[QAOA]
```

## 7. Operation collaboration

```mermaid
flowchart LR
    M[Model and target Curve]
    OC[Operation catalog]
    CAP{Operation Capability<br/>supports Model?}
    REJ[Operation incompatibility evidence]
    OP[Compatible Operation]
    SOL[Operation filters compatible Solvers]
    PREP[Operation.prepare Model configuration]
    REQ[Solver-native request]

    M --> CAP
    OC --> CAP
    CAP -->|no| REJ
    CAP -->|yes| OP
    OP --> SOL
    OP --> PREP --> REQ
```

## 8. Capability-driven Strategy construction

```mermaid
flowchart LR
    D[Domain]
    I[Interpretation Objective Curve]
    F[Catalog formulations]
    M[Compatible Models]
    O[Compatible Operations]
    S[Compatible Solvers]
    ST[Immutable Strategy<br/>Formulation Model Operation Solver Configuration]
    FP[Fingerprint<br/>model operation solver config seed budget]
    A[Analysis<br/>ordered Strategies]

    D --> I
    I --> M
    F --> M
    M --> O --> S --> ST --> FP
    ST --> A
    I --> A
```

## 9. Max-Cut reference path

```mermaid
flowchart LR
    D[MaxCut aggregate]
    O[Binary quadratic Objective]
    M[Direct QUBO Model]
    E[ExactSearch and exact solver]
    A[Annealing and annealing solver]
    X[Execution records]
    C[MaxCut Candidates]
    V[MaxCut Evaluations]
    U[Utility]
    P[Stop Switch Scale]
    R[Recommendation and artifacts]

    D --> O --> M
    M --> E --> X
    M --> A --> X
    X --> C --> V --> U --> P --> R
```

## 10. Portfolio and Vanguard path

```mermaid
flowchart LR
    D[Portfolio aggregate]
    O[Risk return cost Objective with guardrails]
    CQM[CQM or quadratic program Model]
    QUBO[Penalty QUBO Model]
    H[Hamiltonian Model]
    CO[ContinuousOptimization classical reference]
    EX[Bounded ExactSearch reference]
    AN[Annealing]
    QA[QAOA]
    X[Execution records]
    E[Portfolio Evaluations]
    U[Utility comparison]
    P[Stop Switch Scale]
    R[Recommendation evidence and artifacts]

    D --> O
    O --> CQM
    O --> QUBO
    O --> H
    CQM --> CO --> X
    CQM --> EX --> X
    QUBO --> AN --> X
    H --> QA --> X
    X --> E --> U --> P --> R
```

## 11. Ownership boundaries

```mermaid
flowchart LR
    subgraph DS[Domain semantics]
        D[Domain]
        I[Interpretation]
        C[Candidate]
        E[Evaluation]
        D --> I
        C --> D --> E
    end

    subgraph MS[Mathematical structure]
        O[Objective]
        X[Expression]
        CV[Curve]
        F[Formulation]
        M[Model and Decoder]
        O --> X --> CV
        O --> F --> M
    end

    subgraph ES[Execution plugins]
        OP[Operation]
        S[Solver]
        NR[Native Result]
        OP --> S --> NR
    end

    subgraph CS[Evidence and control]
        ST[Strategy]
        EXE[Execution]
        U[Utility]
        P[Policy Decision]
        R[Recommendation]
        ST --> EXE --> U --> P --> R
    end

    I --> O
    M --> OP
    M --> ST
    OP --> ST
    S --> ST
    NR --> M
    M --> C
    E --> EXE
```

## 12. Compatibility lattice

```mermaid
flowchart LR
    MC[MaxCut]
    PD[Portfolio bounded discrete]
    PC[Portfolio continuous]
    SD[Scientific field domain planned]

    DQ[Direct QUBO]
    PQ[Penalty QUBO]
    CQM[CQM or quadratic program]
    H[Hamiltonian or Ising]
    OM[Operator or surrogate Model planned]

    EX[ExactSearch]
    CO[ContinuousOptimization]
    AN[Annealing]
    QA[QAOA]
    SI[Surrogate train or infer planned]

    MC --> DQ
    MC --> H
    PD --> CQM
    PD --> PQ
    PD --> H
    PC --> CQM
    SD -.-> OM

    DQ --> EX
    DQ --> AN
    PQ --> EX
    PQ --> AN
    CQM --> EX
    CQM --> CO
    H --> QA
    OM -.-> SI
```
