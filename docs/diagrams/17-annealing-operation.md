# Annealing operation

[Back to diagram atlas](../README.md)

## 17. Annealing operation

Annealing prepares a binary quadratic model, sampling configuration, and seed or hardware parameters for a compatible sampler.

```mermaid
flowchart LR
    M["Binary quadratic unconstrained Model"]
    CAP{"Annealing supports<br/>target Curve?"}
    BQM["Prepare BQM / QUBO payload"]
    CFG["Reads, seed, schedule,<br/>chain or hardware parameters"]
    REQ["Sampler request"]
    S["Compatible Solver<br/>local simulated annealer<br/>or D-Wave sampler"]
    NR["Sample set and backend metadata"]
    C["Model.decode(best or selected sample)"]
    DC["Domain Candidate"]

    M --> CAP
    CAP -->|yes| BQM --> REQ
    CFG --> REQ
    REQ --> S --> NR --> C --> DC
```

