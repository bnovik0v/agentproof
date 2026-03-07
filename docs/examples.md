# Examples

## Manual LLM-style verification

```python
from agentproof import AgentResponse, ChallengeSpec, generate_challenge, verify_response

challenge = generate_challenge(
    ChallengeSpec(
        challenge_type="obfuscated_text_lock",
        difficulty=2,
        options={"template": "amber_sort"},
    )
)

# Send challenge.to_dict() to the client.
response = AgentResponse(
    challenge_id=challenge.challenge_id,
    challenge_type=challenge.challenge_type,
    payload={"answer": str(challenge.private_data["expected_answer"])},
)

result = verify_response(challenge, response)

assert result.ok
```

## Harder multi-pass example

```python
from agentproof import AgentResponse, ChallengeSpec, generate_challenge, verify_response

challenge = generate_challenge(
    ChallengeSpec(
        challenge_type="multi_pass_lock",
        difficulty=2,
        options={"template": "warm_reverse_length"},
    )
)

response = AgentResponse(
    challenge_id=challenge.challenge_id,
    challenge_type=challenge.challenge_type,
    payload={"answer": str(challenge.private_data["expected_answer"])},
)

result = verify_response(challenge, response)

assert result.ok
```

## Public challenge JSON

```python
public_payload = challenge.to_dict()
internal_payload = challenge.to_internal_dict()
```

`public_payload` does not include the expected answer.
`internal_payload` does.

## CLI generation for the obfuscated family

```bash
agentproof generate obfuscated_text_lock \
  --difficulty 2 \
  --template amber_sort \
  --output challenge.internal.json \
  --public-output challenge.public.json
```

## CLI generation for the harder family

```bash
agentproof generate multi_pass_lock \
  --difficulty 2 \
  --template warm_reverse_length \
  --output challenge.internal.json \
  --public-output challenge.public.json
```

## Benchmark report

```python
from agentproof import run_benchmark

report = run_benchmark(
    challenge_type="obfuscated_text_lock",
    iterations=10,
    difficulty=2,
    template="amber_sort",
)

print(report.to_dict())
```

```bash
agentproof benchmark multi_pass_lock --iterations 10 --difficulty 2 --template warm_reverse_length
```

## Baseline family with a bundled solver

```python
from agentproof import ChallengeSpec, generate_challenge, solve_challenge, verify_response

challenge = generate_challenge(
    ChallengeSpec(challenge_type="proof_of_work", difficulty=16, ttl_seconds=120)
)
response = solve_challenge(challenge)
result = verify_response(challenge, response)

assert result.ok
```

## Failure example

If the client sends the wrong format for either LLM family, the result looks like:

```json
{
  "ok": false,
  "reason": "invalid_answer_format",
  "details": {}
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

- generate public LLM-family challenges
- paste a manual LLM response into the editor
- use the bundled solver for the baseline families
- inspect the raw JSON and failure modes
