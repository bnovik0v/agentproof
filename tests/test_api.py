from __future__ import annotations

from datetime import timedelta

import pytest

from agentproof import ChallengeSpec, generate_challenge, solve_challenge, verify_response
from agentproof.exceptions import UnknownChallengeTypeError
from agentproof.models import AgentResponse, Challenge, parse_datetime, utc_now


def test_proof_of_work_roundtrip() -> None:
    challenge = generate_challenge(ChallengeSpec(challenge_type="proof_of_work", difficulty=12))
    response = solve_challenge(challenge)
    result = verify_response(challenge, response)
    assert result.ok
    assert result.reason == "ok"


def test_proof_of_work_rejects_hash_mismatch() -> None:
    challenge = generate_challenge(ChallengeSpec(challenge_type="proof_of_work", difficulty=8))
    response = solve_challenge(challenge)
    broken = AgentResponse(
        challenge_id=response.challenge_id,
        challenge_type=response.challenge_type,
        payload={"nonce": response.payload["nonce"], "hash": "bad"},
    )
    result = verify_response(challenge, broken)
    assert not result.ok
    assert result.reason == "hash_mismatch"


def test_semantic_math_roundtrip() -> None:
    spec = ChallengeSpec(
        challenge_type="semantic_math_lock",
        options={"topic": "security", "word_count": 6},
    )
    challenge = generate_challenge(spec)
    response = solve_challenge(challenge)
    result = verify_response(challenge, response)
    assert result.ok
    assert result.details["word_count"] == 6


def test_semantic_math_rejects_wrong_word_count() -> None:
    spec = ChallengeSpec(
        challenge_type="semantic_math_lock",
        options={"topic": "agents", "word_count": 5},
    )
    challenge = generate_challenge(spec)
    response = AgentResponse(
        challenge_id=challenge.challenge_id,
        challenge_type=challenge.challenge_type,
        payload={"text": "agents coordinate through"},
    )
    result = verify_response(challenge, response)
    assert not result.ok
    assert result.reason == "wrong_word_count"


def test_semantic_math_rejects_missing_required_word() -> None:
    spec = ChallengeSpec(
        challenge_type="semantic_math_lock",
        options={"topic": "verification", "word_count": 5},
    )
    challenge = generate_challenge(spec)
    response = AgentResponse(
        challenge_id=challenge.challenge_id,
        challenge_type=challenge.challenge_type,
        payload={"text": "verification needs metrics metrics metrics"},
    )
    result = verify_response(challenge, response)
    assert not result.ok
    assert result.reason == "required_word_constraint_failed"


def test_unknown_challenge_type_raises() -> None:
    with pytest.raises(UnknownChallengeTypeError):
        generate_challenge(ChallengeSpec(challenge_type="unknown"))


def test_expired_challenge_rejected() -> None:
    challenge = Challenge(
        challenge_id="expired",
        challenge_type="proof_of_work",
        prompt="expired",
        issued_at=(utc_now() - timedelta(minutes=10)).isoformat(),
        expires_at=(utc_now() - timedelta(minutes=5)).isoformat(),
        data={
            "algorithm": "sha256",
            "difficulty": 0,
            "salt": "salt",
            "payload": "expired:salt",
        },
    )
    response = AgentResponse(
        challenge_id="expired",
        challenge_type="proof_of_work",
        payload={"nonce": "0", "hash": "anything"},
    )
    result = verify_response(challenge, response)
    assert not result.ok
    assert result.reason == "challenge_expired"


def test_parse_datetime_requires_timezone() -> None:
    with pytest.raises(ValueError):
        parse_datetime("2026-03-06T12:00:00")
