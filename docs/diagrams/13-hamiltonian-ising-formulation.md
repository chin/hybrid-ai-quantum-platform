# Hamiltonian / Ising formulation

[Back to diagram atlas](../README.md)

## 13. Hamiltonian / Ising formulation

The formulation maps compatible binary decision semantics into a cost Hamiltonian while preserving the decoder back to a domain candidate.

$$
x_i=\frac{1-Z_i}{2}.
$$

```mermaid
flowchart LR
    O["Binary Objective<br/>and source Curve"]
    C{"Hamiltonian Capability<br/>supports Curve?"}
    MAP["Map binary variables<br/>$$x_i=\frac{1-Z_i}{2}$$"]
    COST["Construct cost Hamiltonian"]
    META["Qubit ordering, scaling,<br/>offset, decoder metadata"]
    M["Hamiltonian Model<br/>target Curve and operator payload"]
    Q["Compatible Operation<br/>QAOA"]

    O --> C
    C -->|yes| MAP --> COST --> M --> Q
    MAP --> META --> M
```

