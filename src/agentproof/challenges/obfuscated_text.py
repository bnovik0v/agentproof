"""Obfuscated language challenge aimed at LLM-capable clients."""

from __future__ import annotations

import random
import secrets
from collections.abc import Callable
from typing import cast

from agentproof.exceptions import SolverUnavailableError
from agentproof.models import (
    AgentResponse,
    Challenge,
    ChallengeSpec,
    JSONValue,
    VerificationResult,
    parse_datetime,
    utc_now,
)
from agentproof.utils.obfuscation import obfuscate_prompt

TOKEN_POOL = [
    "lattice",
    "mira",
    "fable",
    "ember",
    "cinder",
    "signal",
    "glyph",
    "vector",
    "harbor",
    "rivet",
    "sable",
    "fluent",
    "mosaic",
    "nimbus",
    "cipher",
    "orbit",
]

VOWEL_PAIR_POOL = [
    "cinder",
    "signal",
    "cipher",
    "orbit",
    "harbor",
    "rivet",
    "glyph",
    "crypt",
]

TemplateBuilder = Callable[[random.Random], tuple[list[str], str]]


class ObfuscatedTextHandler:
    """Generate and verify LLM-capability prompts with exact output rules."""

    def generate(self, spec: ChallengeSpec) -> Challenge:
        challenge_id = secrets.token_hex(8)
        difficulty = self._difficulty_for_spec(spec)
        template_id = self._template_for_spec(spec)
        rng = random.Random(secrets.randbits(64))
        lines, expected_answer = self._template_builders()[template_id](rng)
        prompt, transform_chain = obfuscate_prompt(lines, difficulty=difficulty, rng=rng)
        data: dict[str, JSONValue] = {
            "difficulty": difficulty,
            "profile": "llm_capability_v1",
            "response_contract": {
                "payload.answer": "UPPERCASE ASCII words joined with hyphens",
                "payload.decoded_preview": "optional free-form notes",
            },
        }
        private_data: dict[str, JSONValue] = {
            "expected_answer": expected_answer,
            "canonical_lines": cast(list[JSONValue], lines),
            "template_id": template_id,
            "transform_chain": cast(list[JSONValue], transform_chain),
        }
        return Challenge.create(
            challenge_id=challenge_id,
            challenge_type=spec.challenge_type,
            prompt=prompt,
            ttl_seconds=spec.ttl_seconds,
            data=data,
            private_data=private_data,
        )

    def solve(self, challenge: Challenge) -> AgentResponse:
        raise SolverUnavailableError(
            "obfuscated_text_lock has no built-in solver; send the public "
            "challenge to an LLM-capable client"
        )

    def verify(self, challenge: Challenge, response: AgentResponse) -> VerificationResult:
        if response.challenge_id != challenge.challenge_id:
            return VerificationResult.failure("challenge_id_mismatch")
        if response.challenge_type != challenge.challenge_type:
            return VerificationResult.failure("challenge_type_mismatch")
        if utc_now() > parse_datetime(challenge.expires_at):
            return VerificationResult.failure("challenge_expired")
        answer = response.payload.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            return VerificationResult.failure("missing_answer")
        decoded_preview = response.payload.get("decoded_preview")
        if decoded_preview is not None and not isinstance(decoded_preview, str):
            return VerificationResult.failure("invalid_decoded_preview")
        normalized_answer = answer.strip().upper()
        if not _is_hyphen_answer(normalized_answer):
            return VerificationResult.failure("invalid_answer_format")
        expected_answer = self._expected_answer(challenge)
        if normalized_answer != expected_answer:
            return VerificationResult.failure(
                "answer_mismatch",
                expected_format="UPPERCASE-HYPHENATED",
            )
        return VerificationResult.success(
            answer=normalized_answer,
            template_id=self._template_id(challenge),
            difficulty=challenge.data.get("difficulty"),
        )

    @staticmethod
    def _difficulty_for_spec(spec: ChallengeSpec) -> int:
        difficulty = spec.difficulty or 1
        return max(1, min(3, difficulty))

    @staticmethod
    def _template_for_spec(spec: ChallengeSpec) -> str:
        template_id = spec.options.get("template", "amber_sort")
        if not isinstance(template_id, str):
            raise ValueError("template must be a string")
        if template_id not in ObfuscatedTextHandler._template_builders():
            raise ValueError(f"unsupported obfuscated_text_lock template: {template_id}")
        return template_id

    @staticmethod
    def _template_builders() -> dict[str, TemplateBuilder]:
        return {
            "amber_sort": _build_amber_sort,
            "echo_reverse": _build_echo_reverse,
            "vowel_count": _build_vowel_count,
        }

    @staticmethod
    def _expected_answer(challenge: Challenge) -> str:
        expected_answer = challenge.private_data.get("expected_answer")
        if not isinstance(expected_answer, str):
            raise ValueError("obfuscated_text_lock challenge is missing private expected_answer")
        return expected_answer

    @staticmethod
    def _template_id(challenge: Challenge) -> str:
        template_id = challenge.private_data.get("template_id")
        if not isinstance(template_id, str):
            raise ValueError("obfuscated_text_lock challenge is missing private template_id")
        return template_id


def _build_amber_sort(rng: random.Random) -> tuple[list[str], str]:
    amber_words = rng.sample(TOKEN_POOL, 3)
    noise_words = rng.sample([word for word in TOKEN_POOL if word not in amber_words], 2)
    entries = [
        ("slot2", "amber", amber_words[0]),
        ("slot1", "amber", amber_words[1]),
        ("slot4", "amber", amber_words[2]),
        ("slot3", "cobalt", noise_words[0]),
        ("slot5", "violet", noise_words[1]),
    ]
    rng.shuffle(entries)
    lines = [
        "decode the drifted brief and answer through payload.answer only",
        "task: keep only shards carrying the amber tag",
        "task: order the kept shard words by slot number from low to high",
        "answer rule: return the shard words in uppercase ascii joined with hyphens",
        *[f"deck: {slot} {tag} {word}" for slot, tag, word in entries],
    ]
    ordered = [word.upper() for slot, tag, word in sorted(entries) if tag == "amber"]
    return lines, "-".join(ordered)


def _build_echo_reverse(rng: random.Random) -> tuple[list[str], str]:
    echo_words = rng.sample(TOKEN_POOL, 3)
    other_words = rng.sample([word for word in TOKEN_POOL if word not in echo_words], 2)
    entries = [
        ("lane1", "echo", echo_words[0]),
        ("lane3", "echo", echo_words[1]),
        ("lane4", "echo", echo_words[2]),
        ("lane2", "moss", other_words[0]),
        ("lane5", "glow", other_words[1]),
    ]
    rng.shuffle(entries)
    lines = [
        "decode the drifted brief and answer through payload.answer only",
        "task: keep only shards carrying the echo mark",
        "task: reverse each kept shard word",
        "task: order the transformed words by lane number from high to low",
        "answer rule: return the transformed words in uppercase ascii joined with hyphens",
        *[f"deck: {lane} {tag} {word}" for lane, tag, word in entries],
    ]
    selected = [
        word[::-1].upper()
        for lane, tag, word in sorted(entries, reverse=True)
        if tag == "echo"
    ]
    return lines, "-".join(selected)


def _build_vowel_count(rng: random.Random) -> tuple[list[str], str]:
    words = rng.sample(VOWEL_PAIR_POOL, 5)
    lines = [
        "decode the drifted brief and answer through payload.answer only",
        "task: keep only shard words whose vowel count is exactly two",
        "task: order the kept shard words by length from short to long and "
        "break ties alphabetically",
        "answer rule: return the kept shard words in uppercase ascii joined with hyphens",
        *[f"deck: shard {word}" for word in words],
    ]
    selected = sorted(
        [word for word in words if _vowel_count(word) == 2],
        key=lambda word: (len(word), word),
    )
    return lines, "-".join(word.upper() for word in selected)


def _vowel_count(word: str) -> int:
    return sum(1 for char in word.lower() if char in "aeiou")


def _is_hyphen_answer(value: str) -> bool:
    parts = value.split("-")
    return bool(parts) and all(part.isalpha() and part.isupper() for part in parts)
