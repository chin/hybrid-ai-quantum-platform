from pathlib import Path

from optengine.domains.maxcut import MaxCut
from optengine.execution import ExecutionInstance
from optengine.explainers.default import DefaultExplainer
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.presets.maxcut import maxcut_catalog
from optengine.utility.operational import OperationalUtility
from optengine.writers.json import JsonRecommendationWriter


a = MaxCut.Vertex(identifier="A")
b = MaxCut.Vertex(identifier="B")

domain = MaxCut(
    name="example",
    graph=MaxCut.Graph(
        vertices=(a, b),
        edges=(MaxCut.Edge(first=a, second=b),),
    ),
)

instance = ExecutionInstance(
    name="maxcut-reference",
    domain=domain,
    catalog=maxcut_catalog(),
    utility=OperationalUtility(),
    policy=ChintropicStopPolicy(),
    explainer=DefaultExplainer(),
    writer=JsonRecommendationWriter(),
    requested_strategies=("max-cut:qubo:exact-search:dimod-exact",),
    output_dir=Path("outputs"),
    render=True,
)

recommendation = instance.execute()
