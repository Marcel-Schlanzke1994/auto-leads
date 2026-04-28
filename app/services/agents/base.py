from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentContext:
    lead_id: int
    website: str | None = None
    channel: str = "email"
    state: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentResult:
    agent_name: str
    status: str
    payload: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class BaseAgent:
    name = "base"

    def run(self, context: AgentContext) -> AgentResult:  # pragma: no cover - interface
        raise NotImplementedError
