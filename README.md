# agentproof

![Distribution](https://img.shields.io/badge/distribution-agentproof--ai-0f766e)
![Python](https://img.shields.io/badge/python-3.10%20to%203.13-1f6feb)
![CI](https://github.com/bnovik0v/agentproof/actions/workflows/ci.yml/badge.svg)
![Docs](https://github.com/bnovik0v/agentproof/actions/workflows/docs.yml/badge.svg)
[![License](https://img.shields.io/github/license/bnovik0v/agentproof)](LICENSE)

![agentproof overview](assets/agentproof-hero.svg)

`agentproof` is a Python library for agent-oriented verification challenges.
It lets a service issue a structured challenge, lets an agent solve it, and verifies the result
deterministically on the server.

Install:

```bash
pip install agentproof-ai
```

Import:

```python
import agentproof
```

## What problem it solves

Traditional CAPTCHA asks "are you human?".

`agentproof` asks a different question:

"Can this client complete an agent-friendly, machine-checkable challenge?"

That is useful when you want to:

- gate agent-focused endpoints
- prototype reverse-CAPTCHA style flows
- add a structured verification step before allowing API access
- experiment with challenge-response systems for LLM agents

## How it works

1. Your server generates a challenge JSON payload.
2. The agent reads it and produces a structured response.
3. Your server verifies the response.
4. Verification returns `ok: true` or a deterministic failure reason.

## Smallest example

```python
from agentproof import ChallengeSpec, generate_challenge, solve_challenge, verify_response

challenge = generate_challenge(
    ChallengeSpec(challenge_type="proof_of_work", difficulty=8, ttl_seconds=60)
)
response = solve_challenge(challenge)
result = verify_response(challenge, response)

assert result.ok
```

## What a real challenge looks like

Example `proof_of_work` challenge:

```json
{
  "challenge_id": "6f2c8e4a91d3b5c1",
  "challenge_type": "proof_of_work",
  "prompt": "Find a nonce such that sha256_hex(payload + ':' + nonce) starts with 8 leading zero bits.",
  "issued_at": "2026-03-07T01:10:00+00:00",
  "expires_at": "2026-03-07T01:11:00+00:00",
  "version": "1",
  "data": {
    "algorithm": "sha256",
    "difficulty": 8,
    "salt": "a14d22b8f91c77e2",
    "payload": "6f2c8e4a91d3b5c1:a14d22b8f91c77e2"
  }
}
```

Example agent response:

```json
{
  "challenge_id": "6f2c8e4a91d3b5c1",
  "challenge_type": "proof_of_work",
  "payload": {
    "nonce": "223",
    "hash": "00bf9b61a372cbd81bef570069b655fd02ef299cc29e9e59d5739e86f5fb6974"
  }
}
```

Example verification result:

```json
{
  "ok": true,
  "reason": "ok",
  "details": {
    "hash": "00bf9b61a372cbd81bef570069b655fd02ef299cc29e9e59d5739e86f5fb6974",
    "nonce": "223"
  }
}
```

## Why this fits agents

These challenges are good for agents because they are:

- machine-readable
- automatable
- exact
- easy to verify on the server

Agents are typically better than humans at:

- reading structured JSON
- following exact constraints
- iterating until a condition is satisfied
- returning properly formatted machine output

## Built-in challenge types

| Challenge type | What the agent does | How it is verified |
| --- | --- | --- |
| `proof_of_work` | Search for a nonce | Recompute hash and check difficulty |
| `semantic_math_lock` | Produce constrained text | Check required words, exact word count, and initial-letter sum |

## Semantic example

```python
from agentproof import ChallengeSpec, generate_challenge, solve_challenge, verify_response

challenge = generate_challenge(
    ChallengeSpec(
        challenge_type="semantic_math_lock",
        ttl_seconds=90,
        options={"topic": "security", "word_count": 7},
    )
)
response = solve_challenge(challenge)
result = verify_response(challenge, response)

print(response.payload["text"])
print(result.to_dict())
```

Typical response text:

```text
security demands careful metrics metrics metrics metrics
```

## API shape

```python
from agentproof import ChallengeSpec, generate_challenge, solve_challenge, verify_response
from agentproof import Challenge, AgentResponse, VerificationResult
```

## CLI

Generate, solve, and verify from the command line:

```bash
agentproof generate proof_of_work --difficulty 16 --output challenge.json
agentproof solve challenge.json --output response.json
agentproof verify challenge.json response.json
```

## Demo

A runnable local demo lives in [`demo/`](https://github.com/bnovik0v/agentproof/tree/main/demo).

Run it with:

```bash
uv run python demo/app.py
```

Then open:

```text
http://127.0.0.1:8765
```

## What this does not prove

`agentproof` does not prove:

- model provenance
- provider identity
- hardware-backed execution
- protection against determined custom automation

It is a challenge-response library, not an identity system.

## Development

```bash
uv sync --extra dev --extra docs --extra demo
uv run ruff check .
uv run mypy .
uv run pytest
uv run python -m build
uv run mkdocs build --strict
```

## Links

- PyPI: https://pypi.org/project/agentproof-ai/
- Docs: https://bnovik0v.github.io/agentproof/
- Demo: [demo/README.md](https://github.com/bnovik0v/agentproof/blob/main/demo/README.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT
