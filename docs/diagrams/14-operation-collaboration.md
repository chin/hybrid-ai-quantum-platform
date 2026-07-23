# Operation collaboration

[Back to diagram atlas](../README.md)

## 14. Operation collaboration

An operation checks the model it receives, filters compatible solvers, and prepares a native request without owning backend execution.

```mermaid
flowchart LR
    M["Model<br/>payload and target Curve"]
    OC["Injected Operation catalog"]
    CAP{"Operation.Capability<br/>supports Model?"}
    REJ["Operation incompatibility evidence"]
    OP["Compatible Operation"]
    SOL["Operation filters compatible Solvers"]
    CFG["Strategy configuration<br/>seed, budget, tolerances"]
    PREP["Operation.prepare(model, configuration)"]
    REQ["Solver-native request"]

    M --> CAP
    OC --> CAP
    CAP -->|no| REJ
    CAP -->|yes| OP --> SOL
    OP --> PREP
    CFG --> PREP --> REQ
```

