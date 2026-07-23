# Execution Instance Guide

`ExecutionInstance` is a named, reusable request for a populated Domain
aggregate and Catalog.

```python
instance = ExecutionInstance(
    name="portfolio-reference",
    domain=portfolio,
    catalog=portfolio_catalog(),
    utility=OperationalUtility(),
    policy=ChintropicStopPolicy(),
    explainer=DefaultExplainer(),
    writer=JsonRecommendationWriter(),
    requested_strategies=(
        "portfolio:cqm:exact-search:dimod-cqm-exact",
        "portfolio:qubo:annealing:dwave-local",
    ),
    output_dir=Path("outputs"),
    render=True,
)
recommendation = instance.execute()
```

The instance does not carry separate generic `input_data`. The Domain object is
already the populated aggregate.

Strategy names are canonical:

```text
domain-type:formulation:operation:solver
```

See [`config/templates/execution_instance.py`](../config/templates/execution_instance.py).
