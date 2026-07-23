# Continuous mean–variance portfolio expression

[Back to diagram atlas](../README.md)

## 09. Continuous mean–variance portfolio expression

The Vanguard classical baseline uses real-valued allocations with a constrained quadratic risk/return objective.

$$
\max_w\; U(w)=\mu^\top w-\lambda w^\top \Sigma w-C_{\mathrm{tx}}(w,w^{(0)})-C_{\mathrm{conc}}(w),
\qquad \mathbf{1}^\top w=1.
$$

```mermaid
flowchart LR
    DATA["Portfolio data<br/>$$\mu,\Sigma,w^{(0)}$$<br/>costs and guardrails"]
    W["Real allocation weights<br/>$$w_i\in[\ell_i,u_i]\subset\mathbb{R}$$"]
    RET["Expected return<br/>$$\mu^\top w$$"]
    RISK["Variance penalty<br/>$$\lambda w^\top\Sigma w$$"]
    TC["Transaction-cost penalty<br/>$$C_{\mathrm{tx}}(w,w^{(0)})$$"]
    CONC["Concentration penalty<br/>$$C_{\mathrm{conc}}(w)$$"]
    CONS["Budget constraint<br/>$$\mathbf{1}^\top w=1$$<br/>bounds, exposure, liquidity, optional cardinality"]
    EX["Continuous quadratic Expression"]
    OBJ["Objective<br/>maximize expected utility"]
    CURVE["Curve<br/>real inputs<br/>degree 2<br/>constrained"]

    DATA --> W
    W --> RET
    W --> RISK
    W --> TC
    W --> CONC
    RET --> EX
    RISK --> EX
    TC --> EX
    CONC --> EX
    CONS --> EX
    EX --> OBJ --> CURVE
```

