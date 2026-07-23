# CQM / quadratic-program formulation

[Back to diagram atlas](../README.md)

## 12. CQM / quadratic-program formulation

A constrained quadratic formulation preserves explicit constraints and supports binary, integer, or real variables where compatible.

$$
\min_x\; x^\top Qx+q^\top x+c
\quad \text{subject to} \quad Ax\le b,\; A_{\mathrm{eq}}x=b_{\mathrm{eq}}.
$$

```mermaid
flowchart LR
    O["Objective<br/>quadratic, possibly constrained"]
    C{"CQM / quadratic-program<br/>Capability supports Curve?"}
    VAR["Preserve compatible variable types<br/>binary, integer, real"]
    CONS["Preserve explicit constraints"]
    PAY["Constrained quadratic payload<br/>$$x^\top Qx+q^\top x+c$$"]
    DEC["Decoder to Domain Candidate"]
    M["CQM / quadratic-program Model"]
    OPS["Compatible Operations<br/>bounded exact, continuous,<br/>constrained hybrid"]

    O --> C
    C -->|yes| VAR --> PAY
    C -->|yes| CONS --> PAY
    PAY --> M
    DEC --> M
    M --> OPS
```

