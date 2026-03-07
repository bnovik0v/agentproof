"""Benchmark helpers for comparing public challenge solvers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from agentproof.api import generate_challenge, verify_response
from agentproof.baselines import get_baseline_solvers
from agentproof.models import ChallengeSpec


@dataclass(frozen=True)
class SolverBenchmark:
    """Summary stats for one baseline solver."""

    solver: str
    solved: int
    attempted: int

    @property
    def success_rate(self) -> float:
        if self.attempted == 0:
            return 0.0
        return self.solved / self.attempted

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["success_rate"] = round(self.success_rate, 4)
        return payload


@dataclass(frozen=True)
class BenchmarkReport:
    """Benchmark results for a challenge family."""

    challenge_type: str
    difficulty: int
    iterations: int
    template: str
    baselines: list[SolverBenchmark]

    def to_dict(self) -> dict[str, Any]:
        return {
            "challenge_type": self.challenge_type,
            "difficulty": self.difficulty,
            "iterations": self.iterations,
            "template": self.template,
            "baselines": [item.to_dict() for item in self.baselines],
        }


def run_benchmark(
    *,
    challenge_type: str,
    iterations: int = 25,
    difficulty: int = 2,
    template: str = "random",
) -> BenchmarkReport:
    """Run baseline solver benchmarks on generated challenges."""
    results: list[SolverBenchmark] = []
    spec = ChallengeSpec(
        challenge_type=challenge_type,
        difficulty=difficulty,
        options={"template": template},
    )
    for solver_name, solver in get_baseline_solvers().items():
        solved = 0
        for _ in range(iterations):
            challenge = generate_challenge(spec)
            response = solver(challenge)
            if response is None:
                continue
            result = verify_response(challenge, response)
            if result.ok:
                solved += 1
        results.append(SolverBenchmark(solver=solver_name, solved=solved, attempted=iterations))
    return BenchmarkReport(
        challenge_type=challenge_type,
        difficulty=difficulty,
        iterations=iterations,
        template=template,
        baselines=results,
    )
