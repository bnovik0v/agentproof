"""Structured text challenge with exact measurable constraints."""

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
from agentproof.utils.normalization import ascii_initial_sum, tokenize_words

TOPIC_WORDS = {
    "agents": ["agents", "coordinate", "through", "clean", "protocols"],
    "security": ["security", "demands", "careful", "threat", "models"],
    "verification": ["verification", "needs", "clear", "rules", "today"],
}

class SemanticMathHandler:
    """Generate and verify text constraints that remain machine-checkable."""

    def generate(self, spec: ChallengeSpec) -> Challenge:
        challenge_id = secrets.token_hex(8)
        topic = self._topic_for_spec(spec)
        required_words = TOPIC_WORDS[topic][:3]
        word_count = self._word_count_for_spec(spec)
        target_sum = sum(ord(word[0]) for word in required_words) + (
            word_count - len(required_words)
        ) * ord("m")
        prompt = (
            f"Write exactly {word_count} words about {topic}. "
            f"Include each required word exactly once: {', '.join(required_words)}. "
            "The ASCII sum of the first letters of all words must equal "
            f"{target_sum}."
        )
        data: dict[str, JSONValue] = {
            "topic": topic,
            "required_words": cast(list[JSONValue], required_words),
            "word_count": word_count,
            "target_initial_sum": target_sum,
        }
        return Challenge.create(
            challenge_id=challenge_id,
            challenge_type=spec.challenge_type,
            prompt=prompt,
            ttl_seconds=spec.ttl_seconds,
            data=data,
        )

    def solve(self, challenge: Challenge) -> AgentResponse:
        required_words = self._required_words(challenge)
        word_count = self._word_count(challenge)
        remaining_count = word_count - len(required_words)
        filler = ["metrics"] * remaining_count
        words = [*required_words, *filler]
        return AgentResponse(
            challenge_id=challenge.challenge_id,
            challenge_type=challenge.challenge_type,
            payload={"text": " ".join(words)},
        )

    def verify(self, challenge: Challenge, response: AgentResponse) -> VerificationResult:
        if response.challenge_id != challenge.challenge_id:
            return VerificationResult.failure("challenge_id_mismatch")
        if response.challenge_type != challenge.challenge_type:
            return VerificationResult.failure("challenge_type_mismatch")
        if utc_now() > parse_datetime(challenge.expires_at):
            return VerificationResult.failure("challenge_expired")

        text = response.payload.get("text")
        if not isinstance(text, str) or not text.strip():
            return VerificationResult.failure("missing_text")

        words = tokenize_words(text)
        required_words = self._required_words(challenge)
        word_count = self._word_count(challenge)
        target_sum = self._target_sum(challenge)

        if len(words) != word_count:
            return VerificationResult.failure(
                "wrong_word_count",
                actual=len(words),
                expected=word_count,
            )

        for required in required_words:
            occurrences = sum(1 for word in words if word.lower() == required)
            if occurrences != 1:
                return VerificationResult.failure(
                    "required_word_constraint_failed",
                    word=required,
                    occurrences=occurrences,
                )

        initial_sum = ascii_initial_sum(words)
        if initial_sum != target_sum:
            return VerificationResult.failure(
                "initial_sum_mismatch",
                actual=initial_sum,
                expected=target_sum,
            )

        topic = challenge.data.get("topic")
        return VerificationResult.success(
            topic=topic,
            word_count=word_count,
            initial_sum=initial_sum,
        )

    @staticmethod
    def _topic_for_spec(spec: ChallengeSpec) -> str:
        topic = spec.options.get("topic", "agents")
        if not isinstance(topic, str):
            raise ValueError("topic must be a string")
        if topic not in TOPIC_WORDS:
            raise ValueError(f"unsupported topic: {topic}")
        return topic

    @staticmethod
    def _word_count_for_spec(spec: ChallengeSpec) -> int:
        word_count = spec.options.get("word_count", 8)
        if not isinstance(word_count, int):
            raise ValueError("word_count must be an integer")
        if word_count < 3:
            raise ValueError("word_count must be at least 3")
        return word_count

    @staticmethod
    def _required_words(challenge: Challenge) -> list[str]:
        required_words = challenge.data.get("required_words")
        if not isinstance(required_words, list) or not all(
            isinstance(item, str) for item in required_words
        ):
            raise ValueError("required_words must be a list of strings")
        return [item for item in required_words if isinstance(item, str)]

    @staticmethod
    def _word_count(challenge: Challenge) -> int:
        word_count = challenge.data.get("word_count")
        if not isinstance(word_count, int):
            raise ValueError("word_count must be an integer")
        return word_count

    @staticmethod
    def _target_sum(challenge: Challenge) -> int:
        target_sum = challenge.data.get("target_initial_sum")
        if not isinstance(target_sum, int):
            raise ValueError("target_initial_sum must be an integer")
        return target_sum
