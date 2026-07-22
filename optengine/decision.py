from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Mapping


@dataclass(frozen=True, kw_only=True)
class Decision:
    selected_strategy: str | None
    reason_code: str
    evidence: Mapping[str, Any] = field(default_factory=dict)
    next_strategy: str | None = None
    resource_change: Mapping[str, Any] = field(default_factory=dict)

    action: ClassVar[str]
    should_continue: ClassVar[bool]

    @property
    def next_action(self) -> str:
        return self.action

    def render(self) -> str:
        return self.action

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "action": self.action,
            "selected_strategy": self.selected_strategy,
            "reason_code": self.reason_code,
            "evidence": dict(self.evidence),
            "next_strategy": self.next_strategy,
            "resource_change": dict(self.resource_change),
            "should_continue": self.should_continue,
        }


class Stop(Decision):
    action = "stop"
    should_continue = False


class Switch(Decision):
    action = "switch"
    should_continue = True


class Scale(Decision):
    action = "scale"
    should_continue = True
