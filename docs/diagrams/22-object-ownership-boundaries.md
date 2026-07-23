# Object ownership boundaries

[Back to diagram atlas](../README.md)

## 22. Object ownership boundaries

The diagram separates semantic meaning, mathematical representation, execution plugins, comparative evidence, control, and persistence.

```mermaid
flowchart LR
    subgraph DS["Domain semantics"]
        D["Domain aggregate"]
        I["Interpretation"]
        C["Candidate"]
        E["Domain Evaluation"]
        D --> I
        C --> D --> E
    end

    subgraph MS["Mathematical representation"]
        O["Objective"]
        X["Expression"]
        CV["Curve"]
        F["Formulation"]
        M["Model and Decoder"]
        O --> X --> CV
        O --> F --> M
    end

    subgraph ES["Execution plugins"]
        OP["Operation"]
        S["Solver"]
        NR["Native Result"]
        OP --> S --> NR
    end

    subgraph CS["Analysis, evidence, and control"]
        ST["Strategy"]
        EXE["Execution"]
        UM["UtilityModel"]
        U["Utility"]
        P["Policy Decision"]
        R["Recommendation"]
        ST --> EXE --> UM --> U --> P --> R
    end

    subgraph PS["Persistence"]
        W["Writer"]
        OUT["JSON and artifacts"]
        W --> OUT
    end

    I --> O
    M --> OP
    M --> ST
    OP --> ST
    S --> ST
    NR --> M
    M --> C
    E --> EXE
    R --> W
```

