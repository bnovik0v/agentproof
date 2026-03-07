from __future__ import annotations

from agentproof import run_benchmark


def test_run_benchmark_for_obfuscated_text_lock() -> None:
    report = run_benchmark(
        challenge_type="obfuscated_text_lock",
        iterations=4,
        difficulty=2,
        template="amber_sort",
    )
    payload = report.to_dict()
    assert payload["challenge_type"] == "obfuscated_text_lock"
    assert payload["iterations"] == 4
    assert len(payload["baselines"]) == 2
    for baseline in payload["baselines"]:
        assert baseline["attempted"] == 4
        assert 0.0 <= baseline["success_rate"] <= 1.0


def test_run_benchmark_for_multi_pass_lock() -> None:
    report = run_benchmark(
        challenge_type="multi_pass_lock",
        iterations=3,
        difficulty=2,
        template="warm_reverse_length",
    )
    payload = report.to_dict()
    assert payload["challenge_type"] == "multi_pass_lock"
    assert payload["iterations"] == 3
    assert len(payload["baselines"]) == 2
