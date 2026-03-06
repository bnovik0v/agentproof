from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agentproof import AgentResponse, ChallengeSpec, generate_challenge, verify_response
from agentproof.models import Challenge


def issue_challenge() -> dict[str, Any]:
    challenge = generate_challenge(
        ChallengeSpec(challenge_type="proof_of_work", difficulty=16, ttl_seconds=120)
    )
    return challenge.to_dict()


def verify_submission(
    challenge_payload: Mapping[str, Any],
    response_payload: Mapping[str, Any],
) -> dict[str, Any]:
    challenge = Challenge(**dict(challenge_payload))
    response = AgentResponse(**dict(response_payload))
    return verify_response(challenge, response).to_dict()
