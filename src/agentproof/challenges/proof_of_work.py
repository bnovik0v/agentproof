"""Hashcash-style proof-of-work challenge."""

from __future__ import annotations

import secrets
from typing import cast

from agentproof.models import (
    AgentResponse,
    Challenge,
    ChallengeSpec,
    JSONValue,
    VerificationResult,
    parse_datetime,
    utc_now,
)
from agentproof.utils.hashing import hash_has_leading_zero_bits, sha256_hex


class ProofOfWorkHandler:
    """Generate and verify proof-of-work challenges."""

    def generate(self, spec: ChallengeSpec) -> Challenge:
        challenge_id = secrets.token_hex(8)
        salt = secrets.token_hex(8)
        payload = f"{challenge_id}:{salt}"
        prompt = (
            "Find a nonce such that sha256_hex(payload + ':' + nonce) starts with "
            f"{spec.difficulty} leading zero bits."
        )
        data: dict[str, JSONValue] = {
            "algorithm": "sha256",
            "difficulty": spec.difficulty,
            "salt": salt,
            "payload": payload,
        }
        return Challenge.create(
            challenge_id=challenge_id,
            challenge_type=spec.challenge_type,
            prompt=prompt,
            ttl_seconds=spec.ttl_seconds,
            data=data,
        )

    def solve(self, challenge: Challenge) -> AgentResponse:
        payload = self._nonce_payload(challenge)
        difficulty = cast(int, challenge.data["difficulty"])
        nonce = 0
        while True:
            candidate = str(nonce)
            digest = sha256_hex(f"{payload}:{candidate}")
            if hash_has_leading_zero_bits(digest, difficulty):
                return AgentResponse(
                    challenge_id=challenge.challenge_id,
                    challenge_type=challenge.challenge_type,
                    payload={"nonce": candidate, "hash": digest},
                )
            nonce += 1

    def verify(self, challenge: Challenge, response: AgentResponse) -> VerificationResult:
        if response.challenge_id != challenge.challenge_id:
            return VerificationResult.failure("challenge_id_mismatch")
        if response.challenge_type != challenge.challenge_type:
            return VerificationResult.failure("challenge_type_mismatch")
        if utc_now() > parse_datetime(challenge.expires_at):
            return VerificationResult.failure("challenge_expired")
        nonce = response.payload.get("nonce")
        digest = response.payload.get("hash")
        if not isinstance(nonce, str) or not nonce:
            return VerificationResult.failure("missing_nonce")
        if not isinstance(digest, str) or not digest:
            return VerificationResult.failure("missing_hash")
        payload = self._nonce_payload(challenge)
        expected_hash = sha256_hex(f"{payload}:{nonce}")
        if expected_hash != digest:
            return VerificationResult.failure("hash_mismatch", expected_hash=expected_hash)
        difficulty = cast(int, challenge.data["difficulty"])
        if not hash_has_leading_zero_bits(digest, difficulty):
            return VerificationResult.failure("insufficient_difficulty", difficulty=difficulty)
        return VerificationResult.success(hash=digest, nonce=nonce)

    @staticmethod
    def _nonce_payload(challenge: Challenge) -> str:
        payload = challenge.data.get("payload")
        if not isinstance(payload, str):
            raise ValueError("proof_of_work challenge payload must be a string")
        return payload
