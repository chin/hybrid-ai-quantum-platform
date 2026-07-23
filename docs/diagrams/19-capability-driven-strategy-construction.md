# Capability-driven Strategy construction

[Back to diagram atlas](../README.md)

## 19. Capability-driven Strategy construction

Analysis filters injected catalogs polymorphically and records every compatible formulation–model–operation–solver collaboration as an immutable Strategy.

```mermaid
flowchart LR
    D["Domain aggregate"]
    I["domain.interpret()<br/>Interpretation and Objective"]
    F["Catalog.formulations"]
    FE["Each Formulation.express(Objective)"]
    M["Compatible Model[]"]
    O["Model.operations(catalog.operations)"]
    S["Operation.solvers(model, catalog.solvers)"]
    ST["Strategy<br/>Formulation + Model + Operation<br/>+ Solver + Configuration"]
    FP["Strategy fingerprint<br/>model + operation + solver<br/>+ configuration + seed + budget"]
    DD["Deterministic ordering<br/>and duplicate removal"]
    A["Analysis<br/>Interpretation + Strategy[]"]

    D --> I --> FE
    F --> FE --> M --> O --> S --> ST --> FP --> DD --> A
    I --> A
```

