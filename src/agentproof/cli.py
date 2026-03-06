"""Command-line interface for agentproof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast

from agentproof.api import generate_challenge, solve_challenge, verify_response
from agentproof.models import AgentResponse, Challenge, ChallengeSpec


def _write_json(payload: dict[str, Any], output_path: str | None) -> None:
    data = json.dumps(payload, indent=2, sort_keys=True)
    if output_path:
        Path(output_path).write_text(f"{data}\n", encoding="utf-8")
        return
    print(data)


def _read_json(path: str) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return cast(dict[str, Any], data)


def _challenge_from_dict(data: dict[str, Any]) -> Challenge:
    return Challenge(**data)


def _response_from_dict(data: dict[str, Any]) -> AgentResponse:
    return AgentResponse(**data)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentproof",
        description="Agent-oriented verification challenges",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate a challenge")
    generate_parser.add_argument("challenge_type", choices=["proof_of_work", "semantic_math_lock"])
    generate_parser.add_argument("--difficulty", type=int, default=0)
    generate_parser.add_argument("--ttl-seconds", type=int, default=120)
    generate_parser.add_argument("--topic", default="agents")
    generate_parser.add_argument("--word-count", type=int, default=8)
    generate_parser.add_argument("--output")

    solve_parser = subparsers.add_parser("solve", help="Solve a challenge from JSON")
    solve_parser.add_argument("challenge_file")
    solve_parser.add_argument("--output")

    verify_parser = subparsers.add_parser("verify", help="Verify a response against a challenge")
    verify_parser.add_argument("challenge_file")
    verify_parser.add_argument("response_file")
    verify_parser.add_argument("--output")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate":
        options: dict[str, Any] = {}
        if args.challenge_type == "semantic_math_lock":
            options = {"topic": args.topic, "word_count": args.word_count}
        spec = ChallengeSpec(
            challenge_type=args.challenge_type,
            difficulty=args.difficulty,
            ttl_seconds=args.ttl_seconds,
            options=options,
        )
        challenge = generate_challenge(spec)
        _write_json(challenge.to_dict(), args.output)
        return 0

    if args.command == "solve":
        challenge = _challenge_from_dict(_read_json(args.challenge_file))
        response = solve_challenge(challenge)
        _write_json(response.to_dict(), args.output)
        return 0

    challenge = _challenge_from_dict(_read_json(args.challenge_file))
    response = _response_from_dict(_read_json(args.response_file))
    result = verify_response(challenge, response)
    _write_json(result.to_dict(), args.output)
    return result.status_code
