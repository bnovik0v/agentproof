"""Non-LLM baseline solvers used for benchmark comparisons."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import cast

from agentproof.models import AgentResponse, Challenge

BaselineSolver = Callable[[Challenge], AgentResponse | None]

LEET_DECODE = str.maketrans(
    {
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
    }
)


def get_baseline_solvers() -> dict[str, BaselineSolver]:
    """Return the registered non-LLM baseline solvers."""
    return {
        "literal_oldstyle": literal_oldstyle_solver,
        "normalized_rule_parser": normalized_rule_parser,
    }


def literal_oldstyle_solver(challenge: Challenge) -> AgentResponse | None:
    """Solve only the older, highly literal prompt patterns."""
    prompt = challenge.prompt.lower()
    if "keep only shards carrying the amber tag" in prompt:
        matches = re.findall(r"slot(\d+)\s+amber\s+([a-z]+)", prompt)
        if not matches:
            return None
        words = [word.upper() for _, word in sorted((int(slot), word) for slot, word in matches)]
        return _response(challenge, "-".join(words))
    if "keep only shards carrying the echo mark" in prompt:
        matches = re.findall(r"lane(\d+)\s+echo\s+([a-z]+)", prompt)
        if not matches:
            return None
        words = [
            word[::-1].upper()
            for _, word in sorted(
                ((int(lane), word) for lane, word in matches),
                reverse=True,
            )
        ]
        return _response(challenge, "-".join(words))
    if "vowel count is exactly two" in prompt:
        words = re.findall(r"deck:\s+shard\s+([a-z]+)", prompt)
        if not words:
            return None
        selected = sorted(
            [word for word in words if _vowel_count(word) == 2],
            key=lambda word: (len(word), word),
        )
        return _response(challenge, "-".join(word.upper() for word in selected))
    return None


def normalized_rule_parser(challenge: Challenge) -> AgentResponse | None:
    """Attempt to solve via prompt normalization and simple regex rules."""
    normalized = _normalize_prompt(challenge.prompt)
    lines = [line.strip() for line in normalized.splitlines() if line.strip()]
    entries = _parse_entries(lines)
    if not entries:
        return None

    keep_label = _detect_keep_label(lines)
    words_only = keep_label is None and _mentions_two_vowels(lines)

    selected_words: list[tuple[int, str]] | list[str]
    if words_only:
        selected_words = [word for _, _, word in entries if _vowel_count(word) == 2]
    else:
        if keep_label is None:
            return None
        selected_words = [
            (position, word) for position, label, word in entries if label == keep_label
        ]
        if not selected_words:
            return None

    answer_words: list[str]
    if words_only:
        answer_words = cast(list[str], selected_words)
    else:
        answer_words = [word for _, word in cast(list[tuple[int, str]], selected_words)]

    if _mentions_trim_last(lines):
        answer_words = [word[:-1] for word in answer_words]
    if _mentions_clip_first_four(lines):
        answer_words = [word[:4] for word in answer_words]
    if _mentions_reverse(lines):
        answer_words = [word[::-1] for word in answer_words]

    if words_only and _mentions_alpha_desc(lines):
        answer_words = sorted(answer_words, reverse=True)
    elif words_only:
        answer_words = sorted(answer_words, key=lambda word: (len(word), word))
    elif _mentions_high_low(lines):
        paired = list(zip(cast(list[tuple[int, str]], selected_words), answer_words, strict=True))
        answer_words = [word for (_, _), word in sorted(paired, reverse=True)]
    elif _mentions_length_order(lines):
        answer_words = sorted(answer_words, key=lambda word: (len(word), word))
    else:
        paired = list(zip(cast(list[tuple[int, str]], selected_words), answer_words, strict=True))
        answer_words = [word for (_, _), word in sorted(paired)]

    return _response(challenge, "-".join(word.upper() for word in answer_words))


def _normalize_prompt(prompt: str) -> str:
    normalized_lines: list[str] = []
    for raw_line in prompt.lower().splitlines():
        line = re.sub(r"frag@[a-z]\d+\s+\S+\s+", "", raw_line)
        line = line.replace("||", " ").replace("::", " ").replace("^^", " ")
        line = line.replace("~~", " ").replace("##", " ").replace("//", " ")
        line = re.sub(r"[^a-z0-9=\|\s-]", " ", line)
        tokens = [_soft_deleet_token(token) for token in line.split()]
        line = re.sub(r"\s+", " ", " ".join(tokens)).strip()
        if line:
            normalized_lines.append(line)
    return "\n".join(normalized_lines)


def _parse_entries(lines: list[str]) -> list[tuple[int, str, str]]:
    results: list[tuple[int, str, str]] = []
    for line in lines:
        match = re.search(
            r"(rung|perch|step|index|lane|slot)=(\d+)\s+\|\s+label=([a-z]+)\s+\|\s+term=([a-z]+)",
            line,
        )
        if match:
            results.append((int(match.group(2)), match.group(3), match.group(4)))
            continue
        match = re.search(r"(rung|perch|step|index|lane|slot)\s+(\d+)\s+([a-z]+)\s+([a-z]+)", line)
        if match:
            results.append((int(match.group(2)), match.group(3), match.group(4)))
            continue
        match = re.search(r"(entry|card|marker|fragment|piece|shard)=([a-z]+)", line)
        if match:
            results.append((0, "word", match.group(2)))
    return results


def _detect_keep_label(lines: list[str]) -> str | None:
    joined = " ".join(lines)
    amber_aliases = ("warm class", "sunlit band", "ember set", "heated group")
    echo_aliases = ("chorus mark", "returning band", "mirror set", "echo class")
    if "amber" in joined and any(alias in joined for alias in amber_aliases):
        return "amber"
    if "echo" in joined and any(alias in joined for alias in echo_aliases):
        return "echo"
    if "amber" in joined and "retain only" in joined:
        return "amber"
    if "echo" in joined and "retain only" in joined:
        return "echo"
    return None


def _mentions_reverse(lines: list[str]) -> bool:
    return any("mirror each kept" in line or "reverse each" in line for line in lines)


def _mentions_length_order(lines: list[str]) -> bool:
    return any("short to long" in line or "shortest to longest" in line for line in lines)


def _mentions_high_low(lines: list[str]) -> bool:
    return any("high to low" in line or "greatest to least" in line for line in lines)


def _mentions_alpha_desc(lines: list[str]) -> bool:
    return any(
        "reverse alphabetical" in line or "alphabetically descending" in line
        for line in lines
    )


def _mentions_two_vowels(lines: list[str]) -> bool:
    return any(
        "vowel load equals two" in line or "vowel count is exactly two" in line
        for line in lines
    )


def _mentions_trim_last(lines: list[str]) -> bool:
    return any("drop the final letter" in line for line in lines)


def _mentions_clip_first_four(lines: list[str]) -> bool:
    return any("first 4 letters" in line or "first four letters" in line for line in lines)


def _vowel_count(word: str) -> int:
    return sum(1 for char in word.lower() if char in "aeiou")


def _response(challenge: Challenge, answer: str) -> AgentResponse:
    return AgentResponse(
        challenge_id=challenge.challenge_id,
        challenge_type=challenge.challenge_type,
        payload={"answer": answer},
    )


def _soft_deleet_token(token: str) -> str:
    if token.isdigit():
        return token
    if token.startswith(("rung=", "perch=", "step=", "index=", "lane=", "slot=")):
        return token
    return token.translate(LEET_DECODE)
