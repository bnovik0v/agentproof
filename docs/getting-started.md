# Getting Started

## Install

```bash
pip install agentproof-ai
```

The published distribution name is `agentproof-ai`, but the import name is `agentproof`.

## Fastest baseline roundtrip

```python
from agentproof import ChallengeSpec, generate_challenge, solve_challenge, verify_response

challenge = generate_challenge(
    ChallengeSpec(challenge_type="proof_of_work", difficulty=8, ttl_seconds=60)
)
response = solve_challenge(challenge)
result = verify_response(challenge, response)

print(challenge.to_dict())
print(response.to_dict())
print(result.to_dict())
```

Use that when you want a deterministic smoke test with a bundled solver.

## Real obfuscated flow

```python
from agentproof import AgentResponse, ChallengeSpec, generate_challenge, verify_response

challenge = generate_challenge(
    ChallengeSpec(
        challenge_type="obfuscated_text_lock",
        difficulty=2,
        options={"template": "amber_sort"},
    )
)

public_payload = challenge.to_dict()

# Send public_payload to your client.
# The server keeps the original challenge object.
response = AgentResponse(
    challenge_id=challenge.challenge_id,
    challenge_type=challenge.challenge_type,
    payload={"answer": "EMBER-HARBOR-SIGNAL"},
)

result = verify_response(challenge, response)
assert result.ok
```

Important detail:

- `challenge.to_dict()` is safe to send to a client
- `challenge.to_internal_dict()` includes private verification data and should stay server-side

## CLI

### Baseline family

```bash
agentproof generate proof_of_work --difficulty 16 --output challenge.json
agentproof solve challenge.json --output response.json
agentproof verify challenge.json response.json
```

### Obfuscated family

```bash
agentproof generate obfuscated_text_lock \
  --difficulty 2 \
  --template amber_sort \
  --output challenge.internal.json \
  --public-output challenge.public.json
```

The internal file is for your server-side verifier.
The public file is what you hand to the client.

`agentproof solve` intentionally does not support `obfuscated_text_lock`.

## Service flow

In a real application:

1. Your backend generates a challenge.
2. Your backend stores the original challenge or its internal JSON.
3. Your backend sends only the public challenge JSON to the client.
4. The client returns a structured response.
5. Your backend verifies it before allowing the next step.

## Local demo

Run the demo app from the repository root:

```bash
uv run python demo/app.py
```

Then open:

```text
http://127.0.0.1:8765
```

The demo starts with `obfuscated_text_lock` selected and lets you paste a manual LLM response into
the browser before verifying it.
