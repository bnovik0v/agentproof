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
    payload={"answer": "EMBER-HARBOR-SIGNAL"},
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

If the client sends the wrong format for `obfuscated_text_lock`, the result looks like:

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

- generate a public obfuscated challenge
- paste a manual LLM response into the editor
- use the bundled solver for the baseline families
- inspect the raw JSON and failure modes
