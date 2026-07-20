from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import optengine.runner as runner_module
from optengine.decision import Decision
from optengine.explanation import Explanation
from optengine.recommendation import Recommendation


class RecordingWriter:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls
        self.logs_seen: list[str] = []
        self.decision_seen: Decision | None = None
        self.explanation_seen: Explanation | None = None

    def write(
        self,
        recommendation: Recommendation,
        output_dir: Path,
        run_name: str,
    ) -> Path:
        self.calls.append("write")
        self.logs_seen = list(recommendation.logs)
        self.decision_seen = recommendation.decision
        self.explanation_seen = recommendation.explanation

        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"{run_name}.json"
        recommendation.output_path = str(path)
        path.write_text("{}", encoding="utf-8")
        return path


def _install_successful_stages(
    monkeypatch: pytest.MonkeyPatch,
    calls: list[str],
) -> None:
    def fake_analyze(engine: Any) -> None:
        calls.append("analyze")

    def fake_evaluate(engine: Any) -> None:
        calls.append("evaluate")

    def fake_decide(engine: Any) -> None:
        calls.append("decide")
        engine.recommendation.decision = Decision(
            action="stop",
            selected_strategy="test-strategy",
            reason_code="TEST_COMPLETE",
            evidence={"quality": 1.0},
        )

    def fake_explain(engine: Any) -> None:
        calls.append("explain")
        engine.recommendation.explanation = Explanation(
            summary="Runner lifecycle completed.",
            selected_strategy="test-strategy",
            evidence={"quality": 1.0},
        )

    monkeypatch.setattr(runner_module, "analyze", fake_analyze)
    monkeypatch.setattr(runner_module, "evaluate", fake_evaluate)
    monkeypatch.setattr(runner_module, "decide", fake_decide)
    monkeypatch.setattr(runner_module, "explain", fake_explain)


def test_run_coordinates_lifecycle_and_returns_recommendation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[str] = []
    _install_successful_stages(monkeypatch, calls)
    writer = RecordingWriter(calls)

    recommendation = runner_module.run(
        {"example": True},
        domain=object(),
        registry=object(),
        policy=object(),
        explainer=object(),
        writer=writer,
        output_dir=tmp_path,
        run_name="runner-smoke",
    )

    assert isinstance(recommendation, Recommendation)
    assert calls == [
        "analyze",
        "evaluate",
        "decide",
        "explain",
        "write",
    ]
    assert recommendation.decision is not None
    assert recommendation.decision.action == "stop"
    assert recommendation.explanation is not None
    assert recommendation.output_path == str(tmp_path / "runner-smoke.json")
    assert Path(recommendation.output_path).exists()


def test_writer_receives_completed_recommendation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[str] = []
    _install_successful_stages(monkeypatch, calls)
    writer = RecordingWriter(calls)

    runner_module.run(
        {"example": True},
        domain=object(),
        registry=object(),
        policy=object(),
        explainer=object(),
        writer=writer,
        output_dir=tmp_path,
        run_name="completed",
    )

    assert writer.decision_seen is not None
    assert writer.explanation_seen is not None
    assert writer.logs_seen == [
        "OptEngine started.",
        "OptEngine finished.",
    ]


def test_stage_failure_stops_later_stages_and_writer(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[str] = []

    def fail_analyze(engine: Any) -> None:
        calls.append("analyze")
        raise RuntimeError("analysis failed")

    monkeypatch.setattr(runner_module, "analyze", fail_analyze)
    monkeypatch.setattr(
        runner_module,
        "evaluate",
        lambda engine: calls.append("evaluate"),
    )
    monkeypatch.setattr(
        runner_module,
        "decide",
        lambda engine: calls.append("decide"),
    )
    monkeypatch.setattr(
        runner_module,
        "explain",
        lambda engine: calls.append("explain"),
    )

    writer = RecordingWriter(calls)

    with pytest.raises(RuntimeError, match="analysis failed"):
        runner_module.run(
            {"example": True},
            domain=object(),
            registry=object(),
            policy=object(),
            explainer=object(),
            writer=writer,
            output_dir=tmp_path,
        )

    assert calls == ["analyze"]


def test_writer_failure_propagates(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[str] = []
    _install_successful_stages(monkeypatch, calls)

    class FailingWriter:
        def write(
            self,
            recommendation: Recommendation,
            output_dir: Path,
            run_name: str,
        ) -> Path:
            raise OSError("write failed")

    with pytest.raises(OSError, match="write failed"):
        runner_module.run(
            {"example": True},
            domain=object(),
            registry=object(),
            policy=object(),
            explainer=object(),
            writer=FailingWriter(),
            output_dir=tmp_path,
        )


def test_render_true_uses_cli_abstraction(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    stage_calls: list[str] = []
    _install_successful_stages(monkeypatch, stage_calls)
    writer = RecordingWriter(stage_calls)

    cli_calls: list[tuple[Any, ...]] = []

    monkeypatch.setattr(
        runner_module,
        "banner",
        lambda title: cli_calls.append(("banner", title)),
        raising=False,
    )
    monkeypatch.setattr(
        runner_module,
        "block",
        lambda label, value, **kwargs: cli_calls.append(
            ("block", label, str(value), kwargs)
        ),
        raising=False,
    )
    monkeypatch.setattr(
        runner_module,
        "footer",
        lambda value: cli_calls.append(("footer", value)),
        raising=False,
    )

    runner_module.run(
        {"example": True},
        domain=object(),
        registry=object(),
        policy=object(),
        explainer=object(),
        writer=writer,
        output_dir=tmp_path,
        render=True,
        title="OptEngine :: Test",
        run_name="render",
    )

    assert cli_calls[0] == ("banner", "OptEngine :: Test")
    labels = [
        call[1]
        for call in cli_calls
        if call[0] == "block"
    ]
    assert labels == [
        "problem",
        "analysis",
        "evaluation",
        "decision",
        "reason",
        "artifact",
    ]
    assert cli_calls[-1] == ("footer", "Runtime Complete")


def test_render_false_makes_no_cli_calls(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    stage_calls: list[str] = []
    _install_successful_stages(monkeypatch, stage_calls)
    writer = RecordingWriter(stage_calls)

    cli_calls: list[tuple[Any, ...]] = []
    monkeypatch.setattr(
        runner_module,
        "banner",
        lambda title: cli_calls.append(("banner", title)),
        raising=False,
    )
    monkeypatch.setattr(
        runner_module,
        "block",
        lambda label, value, **kwargs: cli_calls.append(
            ("block", label, value)
        ),
        raising=False,
    )
    monkeypatch.setattr(
        runner_module,
        "footer",
        lambda value: cli_calls.append(("footer", value)),
        raising=False,
    )

    runner_module.run(
        {"example": True},
        domain=object(),
        registry=object(),
        policy=object(),
        explainer=object(),
        writer=writer,
        output_dir=tmp_path,
        render=False,
    )

    assert cli_calls == []
