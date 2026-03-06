"""Data models used by the public API."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TypeAlias

JSONValue: TypeAlias = None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class ChallengeSpec:
    """Configuration used to issue a challenge."""

    challenge_type: str
    ttl_seconds: int = 120
    difficulty: int = 0
    options: dict[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        if self.difficulty < 0:
            raise ValueError("difficulty must be non-negative")

    def to_dict(self) -> dict[str, JSONValue]:
        return asdict(self)


@dataclass(frozen=True)
class Challenge:
    """Issued challenge payload."""

    challenge_id: str
    challenge_type: str
    prompt: str
    issued_at: str
    expires_at: str
    data: dict[str, JSONValue]
    version: str = "1"

    @classmethod
    def create(
        cls,
        challenge_id: str,
        challenge_type: str,
        prompt: str,
        ttl_seconds: int,
        data: dict[str, JSONValue],
    ) -> Challenge:
        issued_at = utc_now()
        expires_at = issued_at + timedelta(seconds=ttl_seconds)
        return cls(
            challenge_id=challenge_id,
            challenge_type=challenge_type,
            prompt=prompt,
            issued_at=issued_at.isoformat(),
            expires_at=expires_at.isoformat(),
            data=data,
        )

    def to_dict(self) -> dict[str, JSONValue]:
        return asdict(self)


@dataclass(frozen=True)
class AgentResponse:
    """Response submitted by an agent or solver."""

    challenge_id: str
    challenge_type: str
    payload: dict[str, JSONValue]

    def to_dict(self) -> dict[str, JSONValue]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationResult:
    """Structured verification outcome."""

    ok: bool
    reason: str
    details: dict[str, JSONValue] = field(default_factory=dict)

    def to_dict(self) -> dict[str, JSONValue]:
        return asdict(self)

    @property
    def status_code(self) -> int:
        return 0 if self.ok else 1

    @staticmethod
    def success(**details: JSONValue) -> VerificationResult:
        return VerificationResult(ok=True, reason="ok", details=details)

    @staticmethod
    def failure(reason: str, **details: JSONValue) -> VerificationResult:
        return VerificationResult(ok=False, reason=reason, details=details)


def parse_datetime(value: str) -> datetime:
    """Parse an ISO 8601 datetime and ensure it is timezone-aware."""
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("datetime must include timezone information")
    return parsed
