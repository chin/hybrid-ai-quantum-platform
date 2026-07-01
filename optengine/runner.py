import json
from datetime import datetime, timezone

from optengine.ai import analyze
from optengine.optimize import search
from optengine.policy import decide
from optengine.cli import banner, block, footer
from optengine.context import Context
from optengine.solution import Solution


def run(
    problem: str,
    *,
    render: bool = False,
    title: str = "OptEngine :: Runtime",
    run_name: str = "run",
) -> Solution:
    context = Context(problem=problem)
    context.output_dir.mkdir(parents=True, exist_ok=True)

    if render:
        banner(title)
        block("problem", problem)

    context.log("OptEngine started.")

    analyze(context)
    if render:
        block("analysis", "complete", ok=True)

    search(context)
    if render:
        block("search", "complete", ok=True)

    decide(context)
    if render:
        block("decision", context.decision["action"])
        block("reason", context.decision["reason"])

    context.log("OptEngine finished.")

    solution = Solution.from_context(context)
    context.output_path = _write_output(solution, context, run_name=run_name)

    solution = Solution.from_context(context)

    if render:
        block("artifact", solution.output_path)
        footer("Runtime Complete")

    return solution


def _write_output(solution: Solution, context: Context, *, run_name: str):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    output_path = context.output_dir / f"{run_name}_{timestamp}.json"

    payload = {
        "problem": solution.problem,
        "decision": solution.decision,
        "metrics": solution.metrics,
        "results": solution.results,
        "logs": solution.logs,
    }

    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path
