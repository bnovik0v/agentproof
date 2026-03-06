"""Stable public API wrappers."""

from agentproof.challenges import registry
from agentproof.models import AgentResponse, Challenge, ChallengeSpec, VerificationResult


def generate_challenge(spec: ChallengeSpec) -> Challenge:
    """Generate a challenge from a validated challenge specification."""
    handler = registry.get_handler(spec.challenge_type)
    return handler.generate(spec)


def solve_challenge(challenge: Challenge) -> AgentResponse:
    """Solve a challenge using the built-in reference solvers."""
    handler = registry.get_handler(challenge.challenge_type)
    return handler.solve(challenge)


def verify_response(challenge: Challenge, response: AgentResponse) -> VerificationResult:
    """Verify an agent response against a previously issued challenge."""
    handler = registry.get_handler(challenge.challenge_type)
    return handler.verify(challenge, response)

