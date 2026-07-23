# Domain–Formulation–Operation compatibility lattice

[Back to diagram atlas](../README.md)

## 23. Domain–Formulation–Operation compatibility lattice

The lattice summarizes intended compatibility paths; dashed scientific paths are planned extensions rather than current polynomial implementations.

```mermaid
flowchart LR
    subgraph DOM["Domains / source objectives"]
        MC["Max-Cut<br/>binary quadratic"]
        PD["Portfolio<br/>bounded discrete"]
        PC["Portfolio<br/>continuous"]
        SD["Scientific field domain<br/>planned"]
    end

    subgraph FORM["Formulations"]
        DQ["Direct QUBO"]
        PQ["Penalty QUBO"]
        CQM["CQM / quadratic program"]
        H["Hamiltonian / Ising"]
        OM["Operator / surrogate formulation<br/>planned"]
    end

    subgraph OPS["Operations"]
        EX["ExactSearch"]
        CO["ContinuousOptimization"]
        AN["Annealing"]
        QA["QAOA"]
        SI["Surrogate train / infer<br/>planned"]
    end

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

