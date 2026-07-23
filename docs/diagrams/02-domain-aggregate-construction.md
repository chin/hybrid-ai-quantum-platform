# Domain aggregate construction

[Back to diagram atlas](../README.md)

## 02. Domain aggregate construction

Input assembly constructs entities first, resolves relationships second, and then creates the aggregate with object references.

```mermaid
flowchart LR
    RAW["Raw input<br/>configuration, records, identifiers"]
    E1["Pass 1: construct entities<br/>Vertex, Asset, Field, Boundary"]
    IDX["Identity map<br/>stable identifier to object"]
    E2["Pass 2: resolve relationships<br/>Edge, Covariance, Constraint, Coupling"]
    AGG["Domain aggregate<br/>entities plus object relationships"]
    I["domain.interpret()"]
    C["domain.interpret(candidate)"]

    RAW --> E1 --> IDX --> E2 --> AGG
    AGG --> I
    AGG --> C
```

