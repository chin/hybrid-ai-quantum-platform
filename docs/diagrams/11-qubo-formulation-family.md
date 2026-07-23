# QUBO formulation family

[Back to diagram atlas](../README.md)

## 11. QUBO formulation family

Direct QUBO preserves an already compatible objective; penalty QUBO transforms constraints or variable types and must retain validation metadata.

$$
\min_{x\in\{0,1\}^n}\; x^\top Qx + c.
$$

```mermaid
flowchart LR
    O["Objective and source Curve"]

    subgraph DIRECT["Direct QUBO"]
        DC{"Binary, quadratic,<br/>unconstrained?"}
        DP["Preserve coefficients"]
        DM["QUBO Model<br/>$$x^\top Qx+c$$<br/>binary quadratic unconstrained"]
        DC -->|yes| DP --> DM
    end

    subgraph PENALTY["Penalty / discretization QUBO"]
        PC{"Transformable variables<br/>and constraints?"}
        ENC["Discretize variables<br/>and introduce binary encoding"]
        PEN["Convert constraints to<br/>tested penalty terms"]
        PM["QUBO Model<br/>$$x^\top Qx+c$$<br/>target Curve: binary, quadratic, unconstrained"]
        META["Transformation metadata<br/>scaling, penalties, decoder,<br/>validation evidence"]
        PC -->|yes| ENC --> PEN --> PM
        PEN --> META
    end

    O --> DC
    O --> PC
    DM --> EX["ExactSearch or Annealing"]
    PM --> EX
```

