# Formulation collaboration

[Back to diagram atlas](../README.md)

## 10. Formulation collaboration

A formulation checks the source curve, expresses a compatible objective, and returns an immutable model containing the transformed payload and decoder.

```mermaid
flowchart LR
    O["Objective<br/>source Expression and Curve"]
    FC["Injected Formulation catalog"]
    CAP{"Formulation.Capability<br/>supports source Curve?"}
    REJ["Compatibility rejection evidence"]
    EXP["Formulation.express(objective)"]
    TRANS["Transformation<br/>preserve, discretize, penalize,<br/>or map variables"]
    M["Immutable Model<br/>payload, decoder, metadata,<br/>source Curve, target Curve"]
    OPS["Model filters compatible Operations"]

    O --> CAP
    FC --> CAP
    CAP -->|no| REJ
    CAP -->|yes| EXP --> TRANS --> M --> OPS
```

