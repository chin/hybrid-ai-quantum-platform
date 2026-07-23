from __future__ import annotations

from collections.abc import Sequence

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.execution import Execution
from optengine.explanation import Explanation
from optengine.explainers.base import Explainer
from optengine.utility.base import Assessment


class DefaultExplainer(Explainer):
    """Deterministic operational explanation of Stop/Switch/Scale."""

    _SUMMARIES = {
        "NO_FEASIBLE_CANDIDATE": (
            "OptEngine decided to switch because no feasible evaluated "
            "candidate is available."
        ),
        "REFERENCE_TARGET_REACHED": (
            "OptEngine decided to stop because the selected strategy reached "
            "the configured reference target."
        ),
        "LOW_CONFIDENCE": (
            "OptEngine decided to switch because the selected strategy did "
            "not meet the configured confidence threshold."
        ),
        "ADDITIONAL_SEARCH_JUSTIFIED": (
            "OptEngine decided to scale because the selected strategy's "
            "expected improvement justifies additional execution."
        ),
        "MARGINAL_UTILITY_EXHAUSTED": (
            "OptEngine decided to stop because additional execution is not "
            "justified by the current marginal utility."
        ),
    }

    def explain(
        self,
        *,
        decision: Decision,
        executions: Sequence[Execution],
        assessment: Assessment,
        analysis: Analysis,
    ) -> Explanation:
        selected = decision.selected_strategy
        base = self._SUMMARIES.get(
            decision.reason_code,
            f"OptEngine decided to {decision.action} from the available evidence.",
        )
        summary = (
            base
            if selected is None
            else f"{base[:-1]} using strategy '{selected}'."
            if base.endswith(".")
            else f"{base} using strategy '{selected}'."
        )

        alternatives = tuple(
            execution.strategy.name
            for execution in executions
            if execution.strategy.name != selected
        )
        limitations = tuple(
            f"{execution.strategy.name}: {execution.failure.message}"
            for execution in executions
            if execution.failed and execution.failure is not None
        )

        evidence = {
            "reason_code": decision.reason_code,
            "assessment": assessment.to_dict(),
            "strategy_count": len(analysis.strategies),
            "execution_count": len(executions),
            **dict(decision.evidence),
        }
        return Explanation(
            summary=summary,
            selected_strategy=selected,
            evidence=evidence,
            alternatives=alternatives,
            limitations=limitations,
        )
