from __future__ import annotations

import argparse
import json
from pathlib import Path

from optengine.domains.portfolio import Portfolio
from optengine.execution import ExecutionInstance
from optengine.explainers.default import DefaultExplainer
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.presets.portfolio import portfolio_catalog
from optengine.writers.json import JsonRecommendationWriter


def load_instance(path: Path) -> ExecutionInstance:
    payload = json.loads(path.read_text(encoding="utf-8"))
    execution = payload.get("execution", {})
    domain = Portfolio.from_mapping(
        payload["problem"],
        name=str(payload.get("name", "portfolio")),
    )
    return ExecutionInstance(
        name=str(payload.get("name", "portfolio")),
        domain=domain,
        catalog=portfolio_catalog(),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        requested_strategies=tuple(execution.get("strategies", ())) or None,
        output_dir=Path(execution.get("output_dir", "outputs")),
        render=bool(execution.get("render", True)),
        title="OptEngine :: Portfolio Vertical Slice",
        metadata={"config_path": str(path)},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the portfolio vertical slice.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/examples/portfolio.json"),
    )
    args = parser.parse_args()
    recommendation = load_instance(args.config).execute()
    if recommendation.output_path is None:
        raise RuntimeError("Portfolio execution completed without an output path.")


if __name__ == "__main__":
    main()
