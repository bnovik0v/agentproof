"""Prompt obfuscation helpers for LLM-capability challenges."""

from __future__ import annotations

import base64
import random

NOISE_TOKENS = ["//", "::", "~~", "##", "%%", "^^", "||"]
LEET_MAP = str.maketrans(
    {
        "a": "4",
        "e": "3",
        "i": "1",
        "o": "0",
        "s": "5",
        "t": "7",
    }
)


def obfuscate_prompt(
    lines: list[str], *, difficulty: int, rng: random.Random
) -> tuple[str, list[str]]:
    """Render a shuffled, distorted prompt from canonical instruction lines."""
    working = list(lines)
    body = working[1:]
    rng.shuffle(body)
    ordered_lines = [working[0], *body]
    transform_chain = _profile_for_difficulty(difficulty)
    rendered = [_render_line(line, transform_chain, rng) for line in ordered_lines]
    header = f"gl1tch//llm-cap-v1::d{difficulty}"
    footer = "reply via payload.answer only // structured-json"
    return "\n".join([header, *rendered, footer]), transform_chain


def _profile_for_difficulty(difficulty: int) -> list[str]:
    if difficulty <= 1:
        return ["shuffle_lines", "mixed_case", "noise_tokens"]
    if difficulty == 2:
        return ["shuffle_lines", "mixed_case", "noise_tokens", "partial_leetspeak"]
    return [
        "shuffle_lines",
        "mixed_case",
        "noise_tokens",
        "partial_leetspeak",
        "fragment_words",
        "encoded_hint",
    ]


def _render_line(line: str, transform_chain: list[str], rng: random.Random) -> str:
    rendered = line
    if "partial_leetspeak" in transform_chain:
        rendered = _partial_leetspeak(rendered, rng)
    if "fragment_words" in transform_chain:
        rendered = _fragment_words(rendered, rng)
    if "mixed_case" in transform_chain:
        rendered = _mixed_case(rendered, rng)
    if "noise_tokens" in transform_chain:
        rendered = _noise_pad(rendered, rng)
    if "encoded_hint" in transform_chain and "answer rule" in line.lower():
        rendered = f"{rendered} :: b64<{_b64_hint('uppercase hyphen join')}>"
    return rendered


def _partial_leetspeak(line: str, rng: random.Random) -> str:
    parts = line.split()
    transformed: list[str] = []
    for part in parts:
        lowered = part.lower()
        if any(char.isdigit() for char in part) or len(part) <= 3 or rng.random() < 0.45:
            transformed.append(part)
            continue
        candidate = lowered.translate(LEET_MAP)
        transformed.append(candidate if candidate != lowered else part)
    return " ".join(transformed)


def _fragment_words(line: str, rng: random.Random) -> str:
    parts = line.split()
    transformed: list[str] = []
    for part in parts:
        clean = part.strip(",.;")
        if len(clean) < 7 or any(char.isdigit() for char in clean) or rng.random() < 0.5:
            transformed.append(part)
            continue
        split_at = len(clean) // 2
        joiner = rng.choice(NOISE_TOKENS)
        transformed.append(f"{clean[:split_at]}{joiner}{clean[split_at:]}")
    return " ".join(transformed)


def _mixed_case(line: str, rng: random.Random) -> str:
    chars: list[str] = []
    for char in line:
        if not char.isalpha():
            chars.append(char)
            continue
        chars.append(char.upper() if rng.random() < 0.32 else char.lower())
    return "".join(chars)


def _noise_pad(line: str, rng: random.Random) -> str:
    label = f"frag@{rng.choice('abcdef')}{rng.randint(1, 9)}"
    separator = rng.choice(NOISE_TOKENS)
    return f"{label} {separator} {line}"


def _b64_hint(value: str) -> str:
    encoded = base64.b64encode(value.encode("utf-8")).decode("ascii")
    return encoded.rstrip("=")
