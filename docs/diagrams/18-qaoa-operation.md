# QAOA operation

[Back to diagram atlas](../README.md)

## 18. QAOA operation

QAOA prepares the cost operator, mixer, ansatz, optimizer, shots, and depth for a compatible gate-model solver.

$$
\lvert\psi(\boldsymbol{\gamma},\boldsymbol{\beta})\rangle=\prod_{\ell=1}^{p} e^{-i\beta_\ell H_M}e^{-i\gamma_\ell H_C}\lvert+\rangle^{\otimes n}.
$$

```mermaid
flowchart LR
    M["Hamiltonian Model"]
    CAP{"QAOA supports<br/>target Model?"}
    COST["Cost operator<br/>$$H_C$$"]
    MIX["Mixer and initial state<br/>$$H_M,\;\lvert+\rangle^{\otimes n}$$"]
    ANS["Ansatz depth<br/>$$p\in\mathbb{N}$$"]
    OPT["Classical optimizer,<br/>shots, seed, budget"]
    REQ["QAOA execution request"]
    S["Compatible Solver<br/>simulator or QPU adapter"]
    NR["Counts, parameters,<br/>expectation, provenance"]
    C["Model.decode(selected bitstring)"]
    DC["Domain Candidate"]

    M --> CAP
    CAP -->|yes| COST --> REQ
    MIX --> REQ
    ANS --> REQ
    OPT --> REQ
    REQ --> S --> NR --> C --> DC
```

