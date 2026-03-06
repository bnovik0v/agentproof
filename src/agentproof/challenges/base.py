"""Base protocol for challenge handlers."""

from __future__ import annotations

from typing import Protocol

from agentproof.models import AgentResponse, Challenge, ChallengeSpec, VerificationResult


class ChallengeHandler(Protocol):
    """Protocol implemented by each challenge family."""

    def generate(self, spec: ChallengeSpec) -> Challenge:
        ...

    def solve(self, challenge: Challenge) -> AgentResponse:
        ...

    def verify(self, challenge: Challenge, response: AgentResponse) -> VerificationResult:
        ...

