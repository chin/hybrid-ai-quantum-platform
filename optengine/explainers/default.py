from __future__ import annotations

from collections.abc import Sequence

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.evaluation import Evaluation
from optengine.explanation import Explanation
from optengine.explainers.base import Explainer
from optengine.utility.base import UtilityAssessment


class DefaultExplainer(Explainer):
    def explain(
        self,
        decision: Decision,
        evaluations: Sequence[Evaluation],
        assessment: UtilityAssessment | None = None,
        analysis: Analysis | None = None,
    ) -> Explanation:
        strategy = decision.selected_strategy or "no selected strategy"

        summaries = {
            "NO_FEASIBLE_CANDIDATE": (
                "OptEngine decided to switch because no feasible evaluated "
                "candidate is available."
            ),
            "REFERENCE_TARGET_REACHED": (
                f"OptEngine decided to stop with strategy '{strategy}' because "
                "the configured reference target was reached."
            ),
            "LOW_CONFIDENCE": (
                f"OptEngine decided to switch from strategy '{strategy}' because "
                "the evaluation did not meet the confidence threshold."
            ),
            "ADDITIONAL_SEARCH_JUSTIFIED": (
                f"OptEngine decided to scale strategy '{strategy}' because "
                "additional execution is justified by the expected improvement."
            ),
            "MARGINAL_UTILITY_EXHAUSTED": (
                f"OptEngine decided to stop strategy '{strategy}' because "
                "additional execution is not justified by the current marginal utility."
            ),
        }

        summary = summaries.get(
            decision.reason_code,
            (
                f"OptEngine decided to {decision.action} using strategy "
                f"'{strategy}' based on the available evidence."
            ),
        )

        return Explanation(
            summary=summary,
            selected_strategy=decision.selected_strategy,
            evidence=dict(decision.evidence),
            alternatives=tuple(
                evaluation.strategy
                for evaluation in evaluations
                if evaluation.strategy != decision.selected_strategy
            ),
        )
