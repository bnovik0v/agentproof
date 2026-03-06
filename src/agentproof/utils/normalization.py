"""Normalization helpers for deterministic text verification."""

from __future__ import annotations

import re

WORD_RE = re.compile(r"[A-Za-z]+")


def tokenize_words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def ascii_initial_sum(words: list[str]) -> int:
    return sum(ord(word[0].lower()) for word in words if word)

