"""Multi-step obfuscated challenge family for stronger LLM-capability probing."""

from __future__ import annotations

import random
import secrets
from collections.abc import Callable
from typing import cast

from agentproof.challenges.llm_common import (
    AMBER_ALIASES,
    ECHO_ALIASES,
    TOKEN_POOL,
    VOWEL_PAIR_POOL,
    alias_line,
    alpha_desc_order_line,
    choose_lexicon,
    clip_line,
    filter_line,
    high_low_order_line,
    hyphenated_upper,
    is_hyphen_answer,
    length_order_line,
    position_catalog_lines,
    reverse_line,
    trim_tail_line,
    vowel_count,
    vowel_line,
    word_catalog_lines,
)
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

TemplateBuilder = Callable[[random.Random], tuple[list[str], str]]


class MultiPassHandler:
    """Generate harder prompts that require multiple inference/transformation steps."""

    def generate(self, spec: ChallengeSpec) -> Challenge:
        challenge_id = secrets.token_hex(8)
        difficulty = self._difficulty_for_spec(spec)
        template_id = self._template_for_spec(spec)
        rng = random.Random(secrets.randbits(64))
        lines, expected_answer = self._template_builders()[template_id](rng)
        prompt, transform_chain = obfuscate_prompt(lines, difficulty=difficulty, rng=rng)
        data: dict[str, JSONValue] = {
            "difficulty": difficulty,
            "profile": "llm_capability_multi_pass_v1",
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
            "multi_pass_lock has no built-in solver; send the public challenge "
            "to an LLM-capable client"
        )

    def verify(self, challenge: Challenge, response: AgentResponse) -> VerificationResult:
        if response.challenge_id != challenge.challenge_id:
            return VerificationResult.failure("challenge_id_mismatch")
        if response.challenge_type != challenge.challenge_type:
            return VerificationResult.failure("challenge_type_mismatch")
        if utc_now() > parse_datetime(challenge.expires_at):
            return VerificationResult.failure("challenge_expired")
        expected_answer = challenge.private_data.get("expected_answer")
        if not isinstance(expected_answer, str):
            return VerificationResult.failure("missing_private_verification_data")
        template_id = challenge.private_data.get("template_id")
        if not isinstance(template_id, str):
            return VerificationResult.failure("missing_private_verification_data")
        answer = response.payload.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            return VerificationResult.failure("missing_answer")
        normalized_answer = answer.strip().upper()
        if not is_hyphen_answer(normalized_answer):
            return VerificationResult.failure("invalid_answer_format")
        if normalized_answer != expected_answer:
            return VerificationResult.failure(
                "answer_mismatch",
                expected_format="UPPERCASE-HYPHENATED",
            )
        return VerificationResult.success(
            answer=normalized_answer,
            template_id=template_id,
            difficulty=challenge.data.get("difficulty"),
        )

    @staticmethod
    def _difficulty_for_spec(spec: ChallengeSpec) -> int:
        difficulty = spec.difficulty or 2
        return max(1, min(3, difficulty))

    @staticmethod
    def _template_for_spec(spec: ChallengeSpec) -> str:
        template_id = spec.options.get("template", "random")
        if not isinstance(template_id, str):
            raise ValueError("template must be a string")
        if template_id == "random":
            return random.choice(tuple(MultiPassHandler._template_builders()))
        if template_id not in MultiPassHandler._template_builders():
            raise ValueError(f"unsupported multi_pass_lock template: {template_id}")
        return template_id

    @staticmethod
    def _template_builders() -> dict[str, TemplateBuilder]:
        return {
            "warm_reverse_length": _build_warm_reverse_length,
            "echo_clip_desc": _build_echo_clip_desc,
            "vowel_trim_desc": _build_vowel_trim_desc,
        }


def _build_warm_reverse_length(rng: random.Random) -> tuple[list[str], str]:
    lexicon = choose_lexicon(rng)
    alias = rng.choice(AMBER_ALIASES)
    warm_words = rng.sample(TOKEN_POOL, 3)
    noise_words = rng.sample([word for word in TOKEN_POOL if word not in warm_words], 2)
    entries = [
        (2, "amber", warm_words[0]),
        (4, "amber", warm_words[1]),
        (1, "amber", warm_words[2]),
        (3, "cobalt", noise_words[0]),
        (5, "violet", noise_words[1]),
    ]
    rng.shuffle(entries)
    lines = [
        lexicon.intro,
        alias_line(alias, "amber"),
        filter_line(lexicon.entry, alias),
        reverse_line(lexicon.entry),
        length_order_line(rng),
        lexicon.emit,
        lexicon.noise,
        *position_catalog_lines(
            entries,
            board_word=lexicon.board,
            position_word=lexicon.position,
            rng=rng,
        ),
    ]
    transformed = sorted(
        [word[::-1] for _, label, word in entries if label == "amber"],
        key=lambda word: (len(word), word),
    )
    return lines, hyphenated_upper(transformed)


def _build_echo_clip_desc(rng: random.Random) -> tuple[list[str], str]:
    lexicon = choose_lexicon(rng)
    alias = rng.choice(ECHO_ALIASES)
    echo_words = rng.sample(TOKEN_POOL, 3)
    other_words = rng.sample([word for word in TOKEN_POOL if word not in echo_words], 2)
    entries = [
        (1, "echo", echo_words[0]),
        (4, "echo", echo_words[1]),
        (3, "echo", echo_words[2]),
        (2, "glow", other_words[0]),
        (5, "moss", other_words[1]),
    ]
    rng.shuffle(entries)
    lines = [
        lexicon.intro,
        alias_line(alias, "echo"),
        filter_line(lexicon.entry, alias),
        clip_line(lexicon.entry, 4),
        high_low_order_line(lexicon.position, rng),
        lexicon.emit,
        lexicon.noise,
        *position_catalog_lines(
            entries,
            board_word=lexicon.board,
            position_word=lexicon.position,
            rng=rng,
        ),
    ]
    transformed = [
        word[:4]
        for position, label, word in sorted(entries, reverse=True)
        if label == "echo"
    ]
    return lines, hyphenated_upper(transformed)


def _build_vowel_trim_desc(rng: random.Random) -> tuple[list[str], str]:
    lexicon = choose_lexicon(rng)
    words = rng.sample(VOWEL_PAIR_POOL, 5)
    lines = [
        lexicon.intro,
        vowel_line(lexicon.entry),
        trim_tail_line(lexicon.entry),
        alpha_desc_order_line(rng),
        lexicon.emit,
        lexicon.noise,
        *word_catalog_lines(words, board_word=lexicon.board, entry_word=lexicon.entry, rng=rng),
    ]
    transformed = sorted(
        [word[:-1] for word in words if vowel_count(word) == 2],
        reverse=True,
    )
    return lines, hyphenated_upper(transformed)
