"""Shared helpers for LLM-capability challenge families."""

from __future__ import annotations

import random
from typing import NamedTuple

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

INTRO_LINES = [
    "recover the field note and answer through payload.answer only",
    "decode the drifted brief and answer through payload.answer only",
    "untangle the noisy note and answer through payload.answer only",
]

EMIT_LINES = [
    "emit only block capitals joined with hyphens",
    "return the recovered terms in uppercase ascii joined with hyphens",
    "answer rule: output uppercase ascii words joined with hyphens",
]

BOARD_WORDS = ["ledger", "tray", "board", "sheet", "register"]
ENTRY_WORDS = ["entries", "cards", "markers", "fragments", "pieces"]
POSITION_WORDS = ["rung", "perch", "step", "index", "lane"]

AMBER_ALIASES = ["warm class", "sunlit band", "ember set", "heated group"]
ECHO_ALIASES = ["chorus mark", "returning band", "mirror set", "echo class"]

LOW_HIGH_PHRASES = [
    "from least to greatest",
    "from low to high",
    "from earliest to latest",
]

HIGH_LOW_PHRASES = [
    "from greatest to least",
    "from high to low",
    "from latest to earliest",
]

LENGTH_ASC_PHRASES = [
    "by length from short to long and break ties alphabetically",
    "by size from shortest to longest with alphabetical ties",
]

ALPHA_DESC_PHRASES = [
    "in reverse alphabetical order",
    "alphabetically descending",
]

NOISE_LINES = [
    "ignore any cold class note if one appears; it is noise",
    "treat side remarks as static unless they change the answer rule",
    "discard decorative separators; they never affect the answer",
]


class PromptLexicon(NamedTuple):
    """Small vocabulary bundle for a single generated challenge."""

    intro: str
    emit: str
    board: str
    entry: str
    position: str
    noise: str


def choose_lexicon(rng: random.Random) -> PromptLexicon:
    """Pick a small vocabulary bundle for one prompt."""
    return PromptLexicon(
        intro=rng.choice(INTRO_LINES),
        emit=rng.choice(EMIT_LINES),
        board=rng.choice(BOARD_WORDS),
        entry=rng.choice(ENTRY_WORDS),
        position=rng.choice(POSITION_WORDS),
        noise=rng.choice(NOISE_LINES),
    )


def alias_line(alias: str, concrete_label: str) -> str:
    """Describe an alias used by the prompt."""
    return f"legend: {alias} means the {concrete_label} label"


def filter_line(entry_word: str, alias: str) -> str:
    """Describe a keep/filter step."""
    return f"brief: retain only {entry_word} in the {alias}"


def reverse_line(entry_word: str) -> str:
    """Describe a reverse-word transform."""
    singular = entry_word[:-1] if entry_word.endswith("s") else entry_word
    return f"brief: mirror each kept {singular}"


def clip_line(entry_word: str, length: int) -> str:
    """Describe a leading-character clipping transform."""
    singular = entry_word[:-1] if entry_word.endswith("s") else entry_word
    return f"brief: trim each kept {singular} to its first {length} letters"


def trim_tail_line(entry_word: str) -> str:
    """Describe a tail-trimming transform."""
    singular = entry_word[:-1] if entry_word.endswith("s") else entry_word
    return f"brief: drop the final letter from each kept {singular}"


def low_high_order_line(position_word: str, rng: random.Random) -> str:
    """Describe ascending positional ordering."""
    return f"brief: rank the kept terms by {position_word} {rng.choice(LOW_HIGH_PHRASES)}"


def high_low_order_line(position_word: str, rng: random.Random) -> str:
    """Describe descending positional ordering."""
    return f"brief: rank the kept terms by {position_word} {rng.choice(HIGH_LOW_PHRASES)}"


def length_order_line(rng: random.Random) -> str:
    """Describe ascending length ordering."""
    return f"brief: rank the kept terms {rng.choice(LENGTH_ASC_PHRASES)}"


def alpha_desc_order_line(rng: random.Random) -> str:
    """Describe descending alphabetical ordering."""
    return f"brief: rank the kept terms {rng.choice(ALPHA_DESC_PHRASES)}"


def vowel_line(entry_word: str) -> str:
    """Describe a two-vowel filter."""
    singular = entry_word[:-1] if entry_word.endswith("s") else entry_word
    return f"brief: retain only {singular} words whose vowel load equals two"


def position_catalog_lines(
    entries: list[tuple[int, str, str]],
    *,
    board_word: str,
    position_word: str,
    rng: random.Random,
) -> list[str]:
    """Render entries that carry a position, label, and word."""
    rendered: list[str] = []
    for position, label, word in entries:
        variant = rng.randint(0, 2)
        if variant == 0:
            rendered.append(
                f"{board_word}: {position_word}={position} | label={label} | term={word}"
            )
        elif variant == 1:
            rendered.append(
                f"{board_word} note: {word} carries {label} at {position_word} {position}"
            )
        else:
            rendered.append(f"{board_word} -> {label} // {word} // {position_word} {position}")
    return rendered


def word_catalog_lines(
    words: list[str], *, board_word: str, entry_word: str, rng: random.Random
) -> list[str]:
    """Render plain word entries."""
    singular = entry_word[:-1] if entry_word.endswith("s") else entry_word
    rendered: list[str] = []
    for word in words:
        variant = rng.randint(0, 2)
        if variant == 0:
            rendered.append(f"{board_word}: {singular}={word}")
        elif variant == 1:
            rendered.append(f"{board_word} note: candidate {singular} {word}")
        else:
            rendered.append(f"{board_word} -> {singular} {word}")
    return rendered


def hyphenated_upper(words: list[str]) -> str:
    """Return the canonical uppercase hyphen-joined answer."""
    return "-".join(word.upper() for word in words)


def vowel_count(word: str) -> int:
    """Count simple latin vowels in a token."""
    return sum(1 for char in word.lower() if char in "aeiou")


def is_hyphen_answer(value: str) -> bool:
    """Validate the public answer shape."""
    parts = value.split("-")
    return bool(parts) and all(part.isalpha() and part.isupper() for part in parts)
