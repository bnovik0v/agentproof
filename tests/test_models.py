from __future__ import annotations

import pytest

from agentproof.models import ChallengeSpec, VerificationResult


def test_challenge_spec_validates_ttl() -> None:
    with pytest.raises(ValueError):
        ChallengeSpec(challenge_type="proof_of_work", ttl_seconds=0)


def test_challenge_spec_validates_difficulty() -> None:
    with pytest.raises(ValueError):
        ChallengeSpec(challenge_type="proof_of_work", difficulty=-1)


def test_verification_result_status_code() -> None:
    assert VerificationResult.success().status_code == 0
    assert VerificationResult.failure("nope").status_code == 1

