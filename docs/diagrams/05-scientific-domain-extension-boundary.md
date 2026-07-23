# Scientific-domain extension boundary

[Back to diagram atlas](../README.md)

## 05. Scientific-domain extension boundary

A scientific field domain follows the same aggregate and candidate-evaluation pattern while using a future operator/tensor expression profile instead of forcing polynomial semantics.

```mermaid
flowchart LR
    subgraph AGG["Scientific field aggregate — planned"]
        D["ScientificDomain"]
        F["Field definitions"]
        BC["Boundary and initial conditions"]
        DATA["Dataset or observation references"]
        REF["Reference solver or trusted solution"]
        D --> F
        D --> BC
        D --> DATA
        D --> REF
    end

    subgraph INT["Domain interpretation"]
        CALL["domain.interpret()"]
        OBJ["Scientific objective<br/>approximation, residual, or operator learning"]
        OEX["Operator / tensor expression profile<br/>planned extension"]
        CURVE["Compatibility profile<br/>tensor shapes, dimensions,<br/>operators, constraints"]
        CALL --> OBJ --> OEX --> CURVE
    end

    subgraph EVAL["Candidate evaluation"]
        CCALL["domain.interpret(candidate)"]
        C["Scientific Candidate<br/>field, surrogate, or prediction"]
        M["Accuracy, residual, uncertainty,<br/>physical validity, resource evidence"]
        E["Scientific Evaluation"]
        CCALL --> C --> M --> E
    end

    D --> CALL
    D --> CCALL
    OEX -.-> NOTE["Do not represent FNO semantics<br/>as an inaccurate quadratic Expression"]
```

