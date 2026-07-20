from collections.abc import Sequence

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.evaluation import Evaluation
from optengine.explanation import Explanation
from optengine.explainers.base import Explainer


class DefaultExplainer(Explainer):
    def explain(
        self,
        decision: Decision,
        evaluations: Sequence[Evaluation],
        analysis: Analysis,
    ) -> Explanation:
        return Explanation(
            summary=(
                f"OptEngine selected "
                f"{decision.selected_strategy or 'no strategy'} "
                f"and decided to {decision.action}."
            ),
            selected_strategy=(decision.selected_strategy),
            evidence=decision.evidence,
        )
