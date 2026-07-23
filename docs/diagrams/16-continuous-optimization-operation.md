# Continuous-optimization operation

[Back to diagram atlas](../README.md)

## 16. Continuous-optimization operation

Continuous optimization prepares variables, bounds, constraints, objective callbacks, and tolerances for a compatible numerical solver.

```mermaid
flowchart LR
    M["Continuous constrained Model"]
    CAP{"ContinuousOptimization<br/>supports target Curve?"}
    INIT["Initial point and bounds"]
    OBJ["Objective and gradient callbacks"]
    CONS["Constraint callbacks and tolerances"]
    REQ["Numerical optimization request"]
    S["Compatible Solver<br/>SLSQP, trust-constr, COBYLA"]
    NR["Native numerical result"]
    C["Model.decode(native result)"]
    DC["Domain Candidate"]

    M --> CAP
    CAP -->|yes| INIT --> REQ
    OBJ --> REQ
    CONS --> REQ
    REQ --> S --> NR --> C --> DC
```

