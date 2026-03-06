# Examples

## Proof of work

```python
from agentproof import ChallengeSpec, generate_challenge, solve_challenge, verify_response

challenge = generate_challenge(ChallengeSpec(challenge_type="proof_of_work", difficulty=16))
response = solve_challenge(challenge)
result = verify_response(challenge, response)
assert result.ok
```

## Semantic math lock

```python
from agentproof import ChallengeSpec, generate_challenge, solve_challenge

challenge = generate_challenge(
    ChallengeSpec(
        challenge_type="semantic_math_lock",
        options={"topic": "security", "word_count": 7},
    )
)
response = solve_challenge(challenge)
```

