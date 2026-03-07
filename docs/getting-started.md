# Getting Started

## Install

```bash
pip install agentproof-ai
```

The published distribution name is `agentproof-ai`, but the import name is `agentproof`.

## Basic roundtrip

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

## CLI roundtrip

```bash
agentproof generate proof_of_work --difficulty 16 --output challenge.json
agentproof solve challenge.json --output response.json
agentproof verify challenge.json response.json
```

## Service flow

In a real application:

1. Your backend generates a challenge and returns it to the client.
2. The client agent solves it.
3. The client sends the response back.
4. Your backend verifies it before allowing the next step.

## Local demo

Run the demo app from the repository root:

```bash
uv run python demo/app.py
```

Then open:

```text
http://127.0.0.1:8765
```

