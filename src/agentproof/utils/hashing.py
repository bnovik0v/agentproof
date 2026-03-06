"""Hashing utilities."""

from __future__ import annotations

import hashlib


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_has_leading_zero_bits(digest: str, difficulty: int) -> bool:
    if difficulty == 0:
        return True
    binary = bin(int(digest, 16))[2:].zfill(len(digest) * 4)
    return binary.startswith("0" * difficulty)

