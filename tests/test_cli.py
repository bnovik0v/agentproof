from __future__ import annotations

import json
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
