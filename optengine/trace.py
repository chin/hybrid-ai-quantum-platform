from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from optengine.analysis import Analysis
from optengine.cli import blank, detail, heading, item, progress, result
from optengine.decision import Decision
from optengine.execution import Execution
from optengine.mathematics import Constraint, Expression
from optengine.recommendation import Recommendation
from optengine.strategy import Strategy
from optengine.utility.base import Assessment, StrategyAssessment


__all__ = [
    "analysis_chain",
    "assessment_for_execution",
    "execution_result",
    "expression_formula",
    "full_strategy_chain",
    "outcome_chain",
    "render_analysis_chain",
    "render_execution_chain",
    "render_outcome_chain",
    "render_strategy_result",
    "render_strategy_start",
    "render_strategy_utilities",
    "strategy_chain",
    "strategy_selection",
]


_ACRONYMS = {
    "cqm": "CQM",
    "qubo": "QUBO",
    "qpu": "QPU",
    "cpu": "CPU",
    "gpu": "GPU",
}


def _display_name(value: object) -> str:
    text = str(value).strip()
    if not text:
        return "—"
    lowered = text.lower()
    if lowered in _ACRONYMS:
        return _ACRONYMS[lowered]
    if lowered in {"maxcut", "max-cut"}:
        return "Max-Cut"
    parts = text.replace("_", "-").split("-")
    return " ".join(_ACRONYMS.get(part.lower(), part.capitalize()) for part in parts)


def _number(value: object, *, digits: int = 4) -> str:
    if value is None:
        return "—"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number == 0.0:
        return "0"
    if number.is_integer():
        return str(int(number))
    return f"{number:.{digits}g}"


def _duration(seconds: float | None) -> str:
    if seconds is None:
        return "runtime unavailable"
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f} µs"
    if seconds < 1.0:
        return f"{seconds * 1_000:.1f} ms"
    return f"{seconds:.3f} s"


def _percentage(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{100.0 * float(value):.1f}%"


def _variable_name(identifier: object) -> str:
    if isinstance(identifier, str):
        return identifier
    return repr(identifier)


def _term_body(coefficient: float, variables: Sequence[str]) -> str:
    magnitude = abs(float(coefficient))
    variable_text = "·".join(variables)
    if variable_text and magnitude == 1.0:
        return variable_text
    if variable_text:
        return f"{_number(magnitude)}·{variable_text}"
    return _number(magnitude)


def expression_formula(expression: Expression, *, maximum_terms: int = 10) -> str:
    """Render a compact human-readable polynomial without losing term counts."""

    terms: list[tuple[float, tuple[str, ...]]] = []
    if float(expression.constant) != 0.0:
        terms.append((float(expression.constant), ()))
    terms.extend(
        (
            float(term.coefficient),
            (_variable_name(term.variable.identifier),),
        )
        for term in expression.linear_terms
        if float(term.coefficient) != 0.0
    )
    terms.extend(
        (
            float(term.coefficient),
            (
                _variable_name(term.first.identifier),
                _variable_name(term.second.identifier),
            ),
        )
        for term in expression.quadratic_terms
        if float(term.coefficient) != 0.0
    )

    if not terms:
        return "0"

    rendered: list[str] = []
    visible = terms[:maximum_terms]
    for index, (coefficient, variables) in enumerate(visible):
        body = _term_body(coefficient, variables)
        if index == 0:
            rendered.append(f"-{body}" if coefficient < 0 else body)
        else:
            rendered.append(f" {'−' if coefficient < 0 else '+'} {body}")

    hidden = len(terms) - len(visible)
    if hidden:
        rendered.append(f" … ({hidden} more terms)")
    return "".join(rendered)


def _constraint_formula(constraint: Constraint) -> str:
    relation = {"eq": "=", "le": "≤", "ge": "≥"}[constraint.relation]
    expression = Expression(
        variables=tuple(
            dict.fromkeys(
                [term.variable for term in constraint.linear_terms]
                + [
                    variable
                    for term in constraint.quadratic_terms
                    for variable in (term.first, term.second)
                ]
            )
        ),
        linear_terms=constraint.linear_terms,
        quadratic_terms=constraint.quadratic_terms,
        constant=constraint.constant,
    )
    rendered = expression_formula(expression, maximum_terms=6)
    return f"{constraint.name}: {rendered} {relation} {_number(constraint.bound)}"


def _curve_summary(curve: Any) -> str:
    counts: dict[str, int] = {}
    for value_type in curve.input_types:
        key = _display_name(value_type.value).lower()
        counts[key] = counts.get(key, 0) + 1
    inputs = ", ".join(f"{count} {name}" for name, count in counts.items())
    degree = {0: "constant", 1: "linear", 2: "quadratic"}.get(
        curve.degree,
        f"degree {curve.degree}",
    )
    constraints = (
        "unconstrained"
        if not curve.constrained
        else f"{curve.constraint_count} constraint"
        + ("" if curve.constraint_count == 1 else "s")
    )
    input_label = "input" if curve.input_count == 1 else "inputs"
    return f"{inputs} {input_label} → real • {degree} • {constraints}"


def _domain_description(analysis: Analysis) -> str:
    summary = analysis.domain.summary
    domain_type = analysis.domain.domain_type
    if domain_type in {"maxcut", "max-cut"}:
        weighted = "weighted" if summary.get("weighted") else "unweighted"
        parts = [
            f"{summary.get('vertices', 0)} vertices",
            f"{summary.get('edges', 0)} edges",
            weighted,
        ]
        if summary.get("weighted"):
            parts.append(f"total weight {_number(summary.get('total_weight'))}")
        target = dict(summary.get("parameters", {})).get("target_cut_value")
        if target is not None:
            parts.append(f"target ≥ {_number(target)}")
        return " • ".join(parts)

    if domain_type == "portfolio":
        parameters = dict(summary.get("parameters", {}))
        maximum = parameters.get("maximum_assets")
        parts = [
            f"{len(summary.get('assets', ()))} assets",
            f"budget {_number(parameters.get('budget'))}",
            f"increment {_percentage(parameters.get('allocation_increment'))}",
            f"risk aversion {_number(parameters.get('risk_aversion'))}",
        ]
        if maximum is not None:
            parts.append(f"at most {maximum} active assets")
        return " • ".join(parts)

    ignored = {"name", "domain_type"}
    values = [
        f"{key.replace('_', ' ')} {_number(value)}"
        for key, value in summary.items()
        if key not in ignored and not isinstance(value, (Mapping, list, tuple))
    ]
    return " • ".join(values) or "populated domain aggregate"


def _objective_description(analysis: Analysis) -> str:
    objective = analysis.interpretation.objective
    domain_type = analysis.domain.domain_type
    if domain_type in {"maxcut", "max-cut"}:
        return "maximize the weight of edges crossing the two partitions"
    if domain_type == "portfolio":
        risk_aversion = dict(analysis.domain.summary.get("parameters", {})).get(
            "risk_aversion"
        )
        return f"maximize expected return − {_number(risk_aversion)} × covariance risk"
    return f"{objective.sense} {type(objective).__name__}"


def _model_summary(strategy: Strategy) -> str:
    curve = strategy.model.curve
    details = [_curve_summary(curve)]
    source = strategy.model.metadata.get("source")
    if source:
        details.append(f"source {_display_name(source)}")
    return " • ".join(details)


def strategy_selection(strategy: Strategy) -> str:
    reference = " • reference" if strategy.reference else ""
    return (
        f"{_display_name(strategy.formulation.name)} → "
        f"{_display_name(strategy.operation.name)} → "
        f"{_display_name(strategy.solver.name)}{reference}"
    )


def _maxcut_result(execution: Execution) -> tuple[str, str | None]:
    assert execution.evaluation is not None
    metrics = execution.evaluation.metrics
    cut_edges = metrics.get("cut_edges", ())
    result_text = (
        f"cut value {_number(metrics.get('cut_value'))} • "
        f"{len(cut_edges)} crossing edge{'s' if len(cut_edges) != 1 else ''} • "
        f"{'feasible' if execution.evaluation.feasible else 'infeasible'}"
    )
    candidate = execution.candidate
    if candidate is None:
        return result_text, None
    payload = candidate.to_dict()
    selected = ", ".join(map(str, payload.get("selected", ()))) or "∅"
    unselected = ", ".join(map(str, payload.get("unselected", ()))) or "∅"
    return result_text, f"side 1 [{selected}] • side 0 [{unselected}]"


def _portfolio_result(execution: Execution) -> tuple[str, str | None]:
    assert execution.evaluation is not None
    metrics = execution.evaluation.metrics
    result_text = (
        f"utility {_number(metrics.get('utility'))} • "
        f"return {_number(metrics.get('expected_return'))} • "
        f"risk {_number(metrics.get('risk'))} • "
        f"{'feasible' if execution.evaluation.feasible else 'infeasible'}"
    )
    allocations = metrics.get("allocations")
    if not isinstance(allocations, Mapping):
        return result_text, None
    active = [
        (str(name), float(amount))
        for name, amount in allocations.items()
        if abs(float(amount)) > 1e-12
    ]
    active.sort(key=lambda item: (-item[1], item[0]))
    allocation_text = " • ".join(
        f"{name} {_percentage(amount)}" for name, amount in active
    )
    return result_text, allocation_text or "no active allocations"


def _generic_result(execution: Execution) -> tuple[str, str | None]:
    assert execution.evaluation is not None
    evaluation = execution.evaluation
    metrics = evaluation.metrics
    score = metrics.get("score", evaluation.quality)
    result_text = (
        f"quality {_number(score)} • "
        f"{'feasible' if evaluation.feasible else 'infeasible'}"
    )
    candidate = execution.candidate
    if candidate is None:
        return result_text, None
    payload = candidate.to_dict()
    values = payload.get("values")
    if isinstance(values, Mapping):
        return result_text, " • ".join(
            f"{name}={value}" for name, value in values.items()
        )
    return result_text, None


def execution_result(execution: Execution) -> tuple[str, str | None]:
    """Return a domain-aware result sentence and candidate detail."""

    if execution.failed:
        failure = execution.failure
        message = "execution failed"
        if failure is not None:
            message = f"{failure.error_type}: {failure.message}"
        return message, None
    if execution.evaluation is None:
        return "execution completed without an evaluation", None

    domain_type = execution.strategy.domain.domain_type
    if domain_type in {"maxcut", "max-cut"}:
        return _maxcut_result(execution)
    if domain_type == "portfolio":
        return _portfolio_result(execution)
    return _generic_result(execution)


def analysis_chain(analysis: Analysis) -> tuple[tuple[str, Any], ...]:
    """Return the canonical Domain-through-Curve chain."""

    objective = analysis.interpretation.objective
    return (
        ("domain", dict(analysis.domain.summary)),
        ("interpretation", analysis.interpretation.to_dict()),
        ("objective", dict(objective.canonical)),
        ("expression", dict(objective.expression.canonical)),
        ("curve", dict(objective.curve.canonical)),
    )


def strategy_chain(execution: Execution) -> tuple[tuple[str, Any], ...]:
    """Return one Strategy's Formulation-through-Execution chain."""

    strategy = execution.strategy
    return (
        ("formulation", strategy.formulation.signature),
        ("model", strategy.model.to_dict()),
        ("operation", strategy.operation.signature),
        ("solver", strategy.solver.signature),
        ("strategy", strategy.summary()),
        ("execution", execution.to_dict()),
    )


def assessment_for_execution(
    assessment: Assessment,
    execution: Execution,
) -> StrategyAssessment:
    return assessment.for_strategy(execution.strategy.name)


def full_strategy_chain(
    analysis: Analysis,
    execution: Execution,
    assessment: Assessment | None = None,
) -> tuple[tuple[str, Any], ...]:
    """Return one complete observable strategy path."""

    chain = (*analysis_chain(analysis), *strategy_chain(execution))
    if assessment is None:
        return chain
    return (
        *chain,
        ("utility", assessment_for_execution(assessment, execution).to_dict()),
    )


def outcome_chain(
    recommendation: Recommendation,
) -> tuple[tuple[str, Any], ...]:
    """Return the workflow outcome chain after all Strategies execute."""

    assessment = recommendation.assessment
    decision = recommendation.decision
    if assessment is None:
        raise RuntimeError("Recommendation has no Assessment.")
    if decision is None:
        raise RuntimeError("Recommendation has no Decision.")
    return (
        ("utility", assessment.to_dict()),
        ("decision", decision.to_dict()),
        ("recommendation", recommendation.to_dict()),
    )


def render_analysis_chain(analysis: Analysis) -> None:
    """Render the shared mathematical chain and planned strategy selections."""

    objective = analysis.interpretation.objective
    expression = objective.expression

    heading("Problem")
    detail(
        "Domain",
        f"{_display_name(analysis.domain.domain_type)} :: {analysis.domain.name}",
    )
    detail("Definition", _domain_description(analysis))
    detail(
        "Interpretation",
        f"{type(analysis.domain).__name__} → {type(objective).__name__}",
    )
    detail("Objective", _objective_description(analysis))
    detail("Expression", expression_formula(expression))
    if expression.constraints:
        constraints = "\n".join(
            _constraint_formula(constraint) for constraint in expression.constraints[:4]
        )
        hidden = len(expression.constraints) - min(4, len(expression.constraints))
        if hidden:
            constraints += f"\n… {hidden} additional constraints"
        detail("Constraints", constraints)
    detail("Curve", _curve_summary(objective.curve))
    blank()

    heading(f"Strategy plan ({len(analysis.strategies)})")
    for index, strategy in enumerate(analysis.strategies, start=1):
        item(f"{index}.", strategy_selection(strategy))
        detail("Model", _model_summary(strategy), indent=7)
    blank()


def render_strategy_start(
    strategy: Strategy,
    *,
    index: int,
    total: int,
) -> None:
    """Announce one strategy immediately before synchronous execution."""

    heading(f"Strategy {index}/{total}")
    detail("Formulation", _display_name(strategy.formulation.name))
    detail("Model", _model_summary(strategy))
    detail("Operation", _display_name(strategy.operation.name))
    solver = _display_name(strategy.solver.name)
    if strategy.reference:
        solver += " • reference"
    detail("Solver", solver)
    progress(f"Running {solver.replace(' • reference', '')} ...")


def render_strategy_result(
    execution: Execution,
    *,
    index: int,
    total: int,
) -> None:
    """Render the semantic result before the next strategy starts."""

    summary, candidate = execution_result(execution)
    runtime = _duration(execution.runtime_s)
    status = "complete" if execution.succeeded else "failed"
    result(
        f"Execution {status} — {summary} • {runtime}",
        ok=execution.succeeded,
    )
    if candidate:
        detail("Candidate", candidate, indent=4)
    if execution.result is not None and execution.result.native_score is not None:
        detail(
            "Native score",
            _number(execution.result.native_score),
            indent=4,
        )
    if execution.failed and execution.failure is not None:
        detail("Status", "isolated; remaining strategies will continue", indent=4)
    if index < total:
        detail("Next", f"strategy {index + 1}/{total}", indent=4)
    blank()


def render_execution_chain(
    analysis: Analysis,
    executions: Iterable[Execution],
    assessment: Assessment | None = None,
) -> None:
    """Render completed executions as readable strategy cards."""

    del analysis, assessment
    items = tuple(executions)
    for index, execution in enumerate(items, start=1):
        render_strategy_start(
            execution.strategy,
            index=index,
            total=len(items),
        )
        render_strategy_result(
            execution,
            index=index,
            total=len(items),
        )


def _assessment_line(item: StrategyAssessment) -> str:
    if not item.feasible:
        return "infeasible • no utility"
    values = [f"utility {_number(item.utility)}"]
    if item.quality is not None:
        values.append(f"quality {_number(item.quality)}")
    if item.confidence is not None:
        values.append(f"confidence {_percentage(item.confidence)}")
    if item.marginal_utility is not None:
        values.append(f"marginal {_number(item.marginal_utility)}")
    return " • ".join(values)


def render_strategy_utilities(
    executions: Iterable[Execution],
    assessment: Assessment,
) -> None:
    """Render the Utility comparison as a compact ranked list."""

    by_name = {execution.strategy.name: execution for execution in executions}
    heading("Utility ranking")
    for rank, strategy_assessment in enumerate(assessment.ranked, start=1):
        execution = by_name.get(strategy_assessment.strategy)
        selection = (
            strategy_assessment.strategy
            if execution is None
            else strategy_selection(execution.strategy)
        )
        selected = (
            " • selected"
            if strategy_assessment.strategy == assessment.selected_strategy
            else ""
        )
        item(f"{rank}.", selection)
        detail(
            "Utility",
            f"{_assessment_line(strategy_assessment)}{selected}",
            indent=7,
        )
    blank()


def render_outcome_chain(
    recommendation: Recommendation,
    *,
    include_recommendation: bool = False,
) -> None:
    """Render the final Utility → Decision → Recommendation chain."""

    assessment = recommendation.assessment
    decision: Decision | None = recommendation.decision
    if assessment is None or decision is None:
        raise RuntimeError("Recommendation outcome is incomplete.")

    heading("Recommendation")
    selected_execution = next(
        (
            execution
            for execution in recommendation.executions
            if execution.strategy.name == assessment.selected_strategy
        ),
        None,
    )
    selected = (
        "no feasible strategy"
        if assessment.selected_strategy is None
        else assessment.selected_strategy
        if selected_execution is None
        else strategy_selection(selected_execution.strategy)
    )
    detail("Selected", selected)
    detail("Utility", _number(assessment.utility))
    detail("Confidence", _percentage(assessment.confidence))
    detail("Decision", decision.action.upper())
    detail("Reason", decision.reason_code.replace("_", " ").title())

    if include_recommendation and recommendation.explanation is not None:
        why = recommendation.explanation.summary
        if assessment.selected_strategy is not None:
            suffix = f" using strategy '{assessment.selected_strategy}'."
            if why.endswith(suffix):
                why = f"{why[: -len(suffix)]}."
        detail("Why", why)

        failures = [
            (execution.strategy.solver.name, execution.failure.message)
            for execution in recommendation.executions
            if execution.failed and execution.failure is not None
        ]
        if failures:
            detail(
                "Limitations",
                "\n".join(
                    f"{_display_name(solver)}: {message}"
                    for solver, message in failures
                ),
            )
    blank()
