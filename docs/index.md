<div class="hero">
  <div class="hero__copy">
    <div class="hero__eyebrow">agentproof</div>
    <h1>Verification challenges designed for agents, not humans.</h1>
    <p>
      Issue structured challenges, let an agent solve them, and verify the result
      deterministically on the server.
    </p>
    <div class="hero__actions">
      <a class="md-button md-button--primary" href="https://pypi.org/project/agentproof-ai/">PyPI</a>
      <a class="md-button" href="getting-started/">Getting started</a>
      <a class="md-button" href="examples/">Examples</a>
    </div>
  </div>
  <div class="hero__panel">
    <div class="hero__chip">Python 3.10 to 3.13</div>
    <div class="hero__chip">Deterministic verification</div>
    <div class="hero__chip">CLI + API + local demo</div>
    <div class="hero__chip">Published on PyPI</div>
  </div>
</div>

## What it actually does

Traditional CAPTCHA asks whether the client is human.

`agentproof` asks a narrower question:

> Can this client complete an agent-friendly, machine-checkable challenge?

That makes it useful for:

<div class="tile-grid">
  <div class="tile">
    <h3>Agent endpoints</h3>
    <p>Add a structured preflight step before allowing requests to proceed.</p>
  </div>
  <div class="tile">
    <h3>Reverse CAPTCHA experiments</h3>
    <p>Test challenge-response flows that favor automation over manual completion.</p>
  </div>
  <div class="tile">
    <h3>Abuse-control layers</h3>
    <p>Combine deterministic challenges with auth, rate limiting, and replay protection.</p>
  </div>
</div>

## Flow

<div class="step-grid">
  <div class="step-card">
    <strong>1. Issue</strong>
    <p>Your service generates a challenge JSON payload.</p>
  </div>
  <div class="step-card">
    <strong>2. Solve</strong>
    <p>The agent returns a structured response.</p>
  </div>
  <div class="step-card">
    <strong>3. Verify</strong>
    <p>Your service verifies it and returns a deterministic result.</p>
  </div>
</div>

## Smallest working example

```python
from agentproof import ChallengeSpec, generate_challenge, solve_challenge, verify_response

challenge = generate_challenge(
    ChallengeSpec(challenge_type="proof_of_work", difficulty=8, ttl_seconds=60)
)
response = solve_challenge(challenge)
result = verify_response(challenge, response)

assert result.ok
```

## Real request and response

<div class="sample-grid">
  <div class="sample-card">
    <div class="sample-label">Challenge</div>

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

  </div>
  <div class="sample-card">
    <div class="sample-label">Agent response</div>

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

  </div>
</div>

Success result:

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

## Why it fits agents

<div class="reason-grid">
  <div class="reason">
    <h3>Structured</h3>
    <p>Challenges and responses are plain JSON, which agents can parse and emit reliably.</p>
  </div>
  <div class="reason">
    <h3>Exact</h3>
    <p>The rules are measurable: nonce search, word counts, required tokens, exact sums.</p>
  </div>
  <div class="reason">
    <h3>Verifiable</h3>
    <p>The server can explain why a response failed instead of relying on fuzzy scoring.</p>
  </div>
</div>

## What it is not

!!! warning

    `agentproof` is not provider attestation, model identity, or a complete anti-abuse system.
    It is a challenge-response library.

## Continue

- Start with [Getting Started](getting-started.md)
- Compare built-in [Challenge Types](concepts.md)
- Open runnable [Examples](examples.md)
