# Portfolio domain aggregate and candidate evaluation

[Back to diagram atlas](../README.md)

## 04. Portfolio domain aggregate and candidate evaluation

The Portfolio aggregate owns financial semantics, builds a constrained utility objective, and evaluates decoded allocations.

$$
U(w)=\mu^\top w-\lambda w^\top \Sigma w-C_{\mathrm{tx}}(w,w^{(0)})-C_{\mathrm{conc}}(w),
\qquad \mathbf{1}^\top w=1.
$$

```mermaid
flowchart LR
    subgraph AGG["Portfolio aggregate"]
        P["Portfolio"]
        A["Asset[]"]
        C["Covariance[]<br/>Asset object references"]
        G["Guardrails<br/>budget, bounds, exposure,<br/>liquidity, cardinality"]
        H["CurrentHolding[]"]
        P --> A
        P --> C
        P --> G
        P --> H
    end

    subgraph INT["Domain interpretation"]
        CALL["portfolio.interpret()"]
        VAR["Allocation variables<br/>$$w_i\in\mathbb{R}$$ or $$u_i\in\mathbb{Z}_{\ge 0}$$"]
        EX["Utility expression<br/>$$U(w)=\mu^\top w-\lambda w^\top\Sigma w-C_{\mathrm{tx}}-C_{\mathrm{conc}}$$"]
        CON["Guardrails<br/>$$\mathbf{1}^\top w=1$$<br/>bounds, exposure, liquidity, cardinality"]
        OBJ["Objective<br/>maximize expected utility"]
        CURVE["Curve<br/>real, integer, or binary inputs<br/>degree up to 2<br/>constrained"]
        CALL --> VAR --> EX --> OBJ --> CURVE
        CON --> EX
    end

    subgraph EVAL["Candidate evaluation"]
        CCALL["portfolio.interpret(candidate)"]
        CA["Portfolio Candidate<br/>allocation by Asset"]
        CHECK["Validate allocations and guardrails"]
        MET["Compute return, risk, turnover,<br/>concentration, violations"]
        EV["Portfolio Evaluation<br/>objective terms, feasibility, evidence"]
        CCALL --> CA --> CHECK --> MET --> EV
    end

    P --> CALL
    C -.->|risk terms| EX
    G -.->|constraint terms| CON
    P --> CCALL
```

