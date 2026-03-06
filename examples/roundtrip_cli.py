from __future__ import annotations

from agentproof import ChallengeSpec, generate_challenge, solve_challenge, verify_response


def main() -> None:
    challenge = generate_challenge(ChallengeSpec(challenge_type="proof_of_work", difficulty=12))
    response = solve_challenge(challenge)
    result = verify_response(challenge, response)
    print(result.to_dict())


if __name__ == "__main__":
    main()

