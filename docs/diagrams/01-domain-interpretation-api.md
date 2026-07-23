# Domain interpretation API

[Back to diagram atlas](../README.md)

## 01. Domain interpretation API

One public method supports domain interpretation and candidate evaluation while preserving omission versus explicit `None`.

```mermaid
flowchart LR
    A["domain.interpret()<br/>argument omitted"]
    B["domain.interpret(candidate)<br/>candidate supplied"]
    N["domain.interpret(None)<br/>explicit value supplied"]
    D{"One runtime method<br/>omission sentinel"}
    H0["_interpret_domain()"]
    H1["_interpret_candidate(candidate)"]
    I["Interpretation<br/>objective and domain metadata"]
    E["Domain Evaluation<br/>quality, feasibility, evidence"]
    V["Candidate validation path"]

    A --> D
    B --> D
    N --> D
    D -->|argument omitted| H0 --> I
    D -->|argument supplied| H1 --> V --> E
```

