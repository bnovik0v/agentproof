# agentproof

`agentproof` is an open-source Python library for agent-oriented verification challenges.
It helps applications issue deterministic, machine-checkable challenges that are easier for
programmatic agents to solve than for humans to complete manually.

The library does not claim cryptographic proof of model provenance. It focuses on a narrower,
defensible goal: structured challenge-response verification.

## Features

- Typed Python API
- Deterministic challenge generation and verification
- Pluggable challenge families
- Reference CLI for local demos and integration tests
- Testable JSON payloads for web APIs and backend services

## Included challenge families

- `proof_of_work`: a hashcash-style puzzle
- `semantic_math_lock`: a human-readable text challenge with exact measurable constraints

## Installation

```bash
pip install agentproof
```

For local development:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs]"
```

## Quickstart

```python
from agentproof import AgentResponse, ChallengeSpec, generate_challenge, solve_challenge, verify_response

spec = ChallengeSpec(challenge_type="proof_of_work", difficulty=18, ttl_seconds=120)
challenge = generate_challenge(spec)
response = solve_challenge(challenge)
result = verify_response(challenge, response)

assert result.ok
```

## CLI

Generate a challenge:

```bash
agentproof generate proof_of_work --difficulty 18
```

Solve a challenge from a file:

```bash
agentproof solve challenge.json
```

Verify a response:

```bash
agentproof verify challenge.json response.json
```

## Security and scope

`agentproof` is not an identity or attestation system. It does not prove that a request came
from a specific model provider or hardware-backed agent. The current scope is challenge-response
verification with explicit tradeoffs documented in the threat model.

## Development

```bash
ruff check .
ruff format --check .
mypy .
pytest
python -m build
```

## License

MIT

