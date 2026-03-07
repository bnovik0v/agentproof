from __future__ import annotations

import json
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from agentproof.cli import main


def test_cli_roundtrip_proof_of_work(tmp_path: Path) -> None:
    challenge_file = tmp_path / "challenge.json"
    response_file = tmp_path / "response.json"
    result_file = tmp_path / "result.json"

    assert (
        main(["generate", "proof_of_work", "--difficulty", "8", "--output", str(challenge_file)])
        == 0
    )
    assert main(["solve", str(challenge_file), "--output", str(response_file)]) == 0
    assert (
        main(
            [
                "verify",
                str(challenge_file),
                str(response_file),
                "--output",
                str(result_file),
            ]
        )
        == 0
    )

    result = json.loads(result_file.read_text(encoding="utf-8"))
    assert result["ok"] is True


def test_cli_roundtrip_semantic_math(tmp_path: Path) -> None:
    challenge_file = tmp_path / "challenge.json"
    response_file = tmp_path / "response.json"
    result_file = tmp_path / "result.json"

    assert (
        main(
            [
                "generate",
                "semantic_math_lock",
                "--topic",
                "security",
                "--word-count",
                "7",
                "--output",
                str(challenge_file),
            ]
        )
        == 0
    )
    assert main(["solve", str(challenge_file), "--output", str(response_file)]) == 0
    assert (
        main(["verify", str(challenge_file), str(response_file), "--output", str(result_file)])
        == 0
    )

    challenge = json.loads(challenge_file.read_text(encoding="utf-8"))
    response = json.loads(response_file.read_text(encoding="utf-8"))
    result = json.loads(result_file.read_text(encoding="utf-8"))
    assert challenge["challenge_type"] == "semantic_math_lock"
    assert "text" in response["payload"]
    assert result["ok"] is True


def test_cli_generate_obfuscated_public_and_internal_files(tmp_path: Path) -> None:
    internal_file = tmp_path / "challenge.internal.json"
    public_file = tmp_path / "challenge.public.json"
    response_file = tmp_path / "response.json"
    result_file = tmp_path / "result.json"

    assert (
        main(
            [
                "generate",
                "obfuscated_text_lock",
                "--difficulty",
                "2",
                "--template",
                "amber_sort",
                "--output",
                str(internal_file),
                "--public-output",
                str(public_file),
            ]
        )
        == 0
    )

    internal_challenge = json.loads(internal_file.read_text(encoding="utf-8"))
    public_challenge = json.loads(public_file.read_text(encoding="utf-8"))
    assert "private_data" in internal_challenge
    assert "private_data" not in public_challenge

    response = {
        "challenge_id": internal_challenge["challenge_id"],
        "challenge_type": internal_challenge["challenge_type"],
        "payload": {
            "answer": internal_challenge["private_data"]["expected_answer"],
            "decoded_preview": "manual llm test",
        },
    }
    response_file.write_text(json.dumps(response), encoding="utf-8")

    assert (
        main(["verify", str(internal_file), str(response_file), "--output", str(result_file)])
        == 0
    )
    result = json.loads(result_file.read_text(encoding="utf-8"))
    assert result["ok"] is True


def test_cli_solve_obfuscated_returns_nonzero(tmp_path: Path) -> None:
    challenge_file = tmp_path / "challenge.json"
    assert (
        main(
            [
                "generate",
                "obfuscated_text_lock",
                "--output",
                str(challenge_file),
            ]
        )
        == 0
    )
    stderr = StringIO()
    with redirect_stderr(stderr):
        exit_code = main(["solve", str(challenge_file)])
    assert exit_code == 2
    assert "no built-in solver" in stderr.getvalue()
