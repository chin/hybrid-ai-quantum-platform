# Exact-search operation

[Back to diagram atlas](../README.md)

## 15. Exact-search operation

Exact search prepares finite enumeration from the model and delegates native execution to a compatible exact solver.

```mermaid
flowchart LR
    M["Finite Model<br/>bounded variables and constraints"]
    CAP{"ExactSearch supports<br/>target Curve and size?"}
    ENUM["Prepare enumeration request<br/>variable order, domains,<br/>constraints, objective"]
    S["Compatible exact Solver<br/>local enumerator or DimodExact"]
    NR["Native result<br/>best sample and search metadata"]
    C["Model.decode(native result)"]
    DC["Domain Candidate"]

    M --> CAP
    CAP -->|yes| ENUM --> S --> NR --> C --> DC
```

