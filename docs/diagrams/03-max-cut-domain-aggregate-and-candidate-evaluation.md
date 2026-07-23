# Max-Cut domain aggregate and candidate evaluation

[Back to diagram atlas](../README.md)

## 03. Max-Cut domain aggregate and candidate evaluation

The Max-Cut aggregate defines graph meaning, produces a binary quadratic objective, and evaluates decoded partitions.

$$
x_v \in \{0,1\} \quad \forall v \in V,
\qquad
C(x)=\sum_{(u,v)\in E} w_{uv}\left(x_u+x_v-2x_u x_v\right).
$$

```mermaid
flowchart LR
    subgraph AGG["MaxCut aggregate"]
        MC["MaxCut"]
        V["Vertex[]"]
        ED["Edge[]<br/>first Vertex<br/>second Vertex<br/>weight"]
        MC --> V
        MC --> ED
    end

    subgraph INT["Domain interpretation"]
        CALL["max_cut.interpret()"]
        VAR["Binary decision variable<br/>$$x_v \in \{0,1\} \quad \forall v\in V$$"]
        EX["Max-Cut expression<br/>$$C(x)=\sum_{(u,v)\in E}w_{uv}(x_u+x_v-2x_u x_v)$$"]
        OBJ["Objective<br/>maximize cut weight"]
        CURVE["Curve<br/>binary inputs<br/>degree 2<br/>unconstrained"]
        CALL --> VAR --> EX --> OBJ --> CURVE
    end

    subgraph EVAL["Candidate evaluation"]
        CCALL["max_cut.interpret(candidate)"]
        CA["MaxCut Candidate<br/>Vertex to partition 0 or 1"]
        CHECK["Validate complete binary assignment"]
        CROSS["Identify crossing edges"]
        EV["MaxCut Evaluation<br/>cut value, ratio, feasibility, evidence"]
        CCALL --> CA --> CHECK --> CROSS --> EV
    end

    MC --> CALL
    ED -.->|contributes terms| EX
    MC --> CCALL
```

