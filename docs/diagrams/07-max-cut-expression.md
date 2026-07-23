# Max-Cut expression

[Back to diagram atlas](../README.md)

## 07. Max-Cut expression

Each graph vertex becomes a binary variable and each edge contributes linear and quadratic terms to the cut objective.

$$
x_v \in \{0,1\},
\qquad
C(x)=\sum_{(u,v)\in E} w_{uv}\left(x_u+x_v-2x_u x_v\right).
$$

```mermaid
flowchart LR
    G["Weighted graph<br/>$$G=(V,E,w)$$"]
    VAR["Variables<br/>$$x_v \in \{0,1\}$$"]
    EDGE["Per-edge contribution<br/>$$w_{uv}(x_u+x_v-2x_u x_v)$$"]
    EX["Objective expression<br/>$$C(x)=\sum_{(u,v)\in E}w_{uv}(x_u+x_v-2x_u x_v)$$"]
    OBJ["Objective<br/>maximize"]
    CURVE["Curve<br/>binary input count: $$\lvert V\rvert$$<br/>one real output<br/>quadratic<br/>no explicit constraints"]

    G --> VAR
    G --> EDGE
    VAR --> EDGE --> EX --> OBJ --> CURVE
```

