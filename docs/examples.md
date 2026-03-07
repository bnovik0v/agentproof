# Examples

## Proof of work

```python
from agentproof import ChallengeSpec, generate_challenge, solve_challenge, verify_response

challenge = generate_challenge(
    ChallengeSpec(challenge_type="proof_of_work", difficulty=16, ttl_seconds=120)
)
response = solve_challenge(challenge)
result = verify_response(challenge, response)

assert result.ok
```

## Semantic math lock

```python
from agentproof import ChallengeSpec, generate_challenge, solve_challenge, verify_response

challenge = generate_challenge(
    ChallengeSpec(
        challenge_type="semantic_math_lock",
        options={"topic": "security", "word_count": 7},
    )
)
response = solve_challenge(challenge)
result = verify_response(challenge, response)

assert result.ok
print(response.payload["text"])
```

## Manual verification in a service

```python
from agentproof import AgentResponse, Challenge, verify_response

challenge = Challenge(**challenge_payload_from_storage)
response = AgentResponse(**response_payload_from_client)
result = verify_response(challenge, response)

if result.ok:
    allow_request()
else:
    reject_request(result.reason)
```

## Failure example

If the client sends the wrong number of words for `semantic_math_lock`, the result looks like:

```json
{
  "ok": false,
  "reason": "wrong_word_count",
  "details": {
    "actual": 3,
    "expected": 7
  }
}
```

## Local demo

The repository ships a runnable local demo in the
[`demo/` directory on GitHub](https://github.com/bnovik0v/agentproof/tree/main/demo).

Run it with:

```bash
uv run python demo/app.py
```

The demo lets you:

- generate challenges
- auto-solve them
- inspect the raw JSON
- tamper with the response and watch verification fail
