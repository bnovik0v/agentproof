from __future__ import annotations

import pytest

from agentproof.models import Challenge, ChallengeSpec, VerificationResult


def test_challenge_spec_validates_ttl() -> None:
    with pytest.raises(ValueError):
        ChallengeSpec(challenge_type="proof_of_work", ttl_seconds=0)


def test_challenge_spec_validates_difficulty() -> None:
    with pytest.raises(ValueError):
        ChallengeSpec(challenge_type="proof_of_work", difficulty=-1)


def test_verification_result_status_code() -> None:
    assert VerificationResult.success().status_code == 0
    assert VerificationResult.failure("nope").status_code == 1


def test_challenge_public_dict_hides_private_data() -> None:
    challenge = Challenge.create(
        challenge_id="test",
        challenge_type="obfuscated_text_lock",
        prompt="prompt",
        ttl_seconds=60,
        data={"difficulty": 2},
        private_data={"expected_answer": "LATTICE-MIRA-FABLE"},
    )
    public_payload = challenge.to_dict()
    internal_payload = challenge.to_internal_dict()
    assert "private_data" not in public_payload
    private_payload = internal_payload["private_data"]
    assert isinstance(private_payload, dict)
    assert private_payload["expected_answer"] == "LATTICE-MIRA-FABLE"
