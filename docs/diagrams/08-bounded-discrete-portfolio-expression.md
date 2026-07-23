# Bounded discrete portfolio expression

[Back to diagram atlas](../README.md)

## 08. Bounded discrete portfolio expression

The MVP portfolio uses bounded allocation units, optional selectors, a quadratic utility, and explicit constraints.

$$
w_i(u_i)=\Delta_i u_i,
\quad u_i\in\{0,\ldots,U_i\},
\quad z_i\in\{0,1\},
$$

$$
U(u)=\mu^\top w(u)-\lambda w(u)^\top \Sigma w(u)-C_{\mathrm{tx}}(w(u))-C_{\mathrm{conc}}(w(u)),
\qquad \sum_i w_i(u_i)=1.
$$

```mermaid
flowchart LR
    DATA["Portfolio data<br/>expected returns, covariance,<br/>costs, guardrails"]
    U["Integer allocation units<br/>$$u_i\in\{0,\ldots,U_i\}$$"]
    Z["Optional selectors<br/>$$z_i\in\{0,1\}$$"]
    RET["Return reward<br/>$$\mu^\top w(u)$$"]
    RISK["Risk penalty<br/>$$\lambda w(u)^\top\Sigma w(u)$$"]
    COST["Cost penalties<br/>$$C_{\mathrm{tx}}(w(u))+C_{\mathrm{conc}}(w(u))$$"]
    CONS["Budget constraint<br/>$$\sum_i w_i(u_i)=1$$<br/>bounds, cardinality, exposure, liquidity"]
    EX["Quadratic Expression"]
    OBJ["Objective<br/>maximize utility"]
    CURVE["Curve<br/>integer and optional binary inputs<br/>degree 2<br/>constrained"]

    DATA --> U
    DATA --> Z
    U --> RET
    U --> RISK
    U --> COST
    Z --> CONS
    RET --> EX
    RISK --> EX
    COST --> EX
    CONS --> EX
    EX --> OBJ --> CURVE
```

