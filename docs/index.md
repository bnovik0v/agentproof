<div class="hero">
  <div class="hero__copy">
    <div class="hero__eyebrow">agentproof</div>
    <h1>LLM-capability CAPTCHA for obfuscated language challenges.</h1>
    <p>
      Issue a public challenge, keep the private verification copy server-side,
      and check whether a client can recover and execute an obfuscated instruction.
    </p>
    <div class="hero__actions">
      <a class="md-button md-button--primary" href="https://pypi.org/project/agentproof-ai/">PyPI</a>
      <a class="md-button" href="getting-started/">Getting started</a>
      <a class="md-button" href="examples/">Examples</a>
    </div>
  </div>
  <div class="hero__panel">
    <div class="hero__chip">Python 3.10 to 3.13</div>
    <div class="hero__chip">Public challenge + private verifier copy</div>
    <div class="hero__chip">Structured JSON answers</div>
    <div class="hero__chip">CLI + API + benchmark harness + local demo</div>
  </div>
</div>

## What it actually does

Traditional CAPTCHA asks whether the client is human.

`agentproof` asks a narrower question:

> Can this client recover and execute an obfuscated instruction in an LLM-like way?

That makes it useful for:

<div class="tile-grid">
  <div class="tile">
    <h3>LLM-first endpoints</h3>
    <p>Add a capability gate before exposing agent-focused routes.</p>
  </div>
  <div class="tile">
    <h3>Reverse CAPTCHA experiments</h3>
    <p>Favor clients that can decode noisy instructions and answer in exact JSON.</p>
  </div>
  <div class="tile">
    <h3>Composable verification</h3>
    <p>Combine challenge-response checks with auth, replay protection, and rate limits.</p>
  </div>
</div>

## Flow

<div class="step-grid">
  <div class="step-card">
    <strong>1. Issue</strong>
    <p>Your service generates a challenge and keeps the internal verification copy.</p>
  </div>
  <div class="step-card">
    <strong>2. Send</strong>
    <p>The client receives only the public challenge JSON with the obfuscated prompt.</p>
  </div>
  <div class="step-card">
    <strong>3. Verify</strong>
    <p>Your service checks the returned JSON answer against the private expected result.</p>
  </div>
</div>

## Smallest working example

```python
from agentproof import AgentResponse, ChallengeSpec, generate_challenge, verify_response

challenge = generate_challenge(
    ChallengeSpec(
        challenge_type="obfuscated_text_lock",
        difficulty=2,
        options={"template": "amber_sort"},
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

When you need a stronger language-recovery task, generate `multi_pass_lock` instead. It keeps the
same verification model but adds multiple rule and transformation stages.

## Real public challenge and response

<div class="sample-grid">
  <div class="sample-card">
    <div class="sample-label">Challenge</div>

```json
{
  "challenge_id": "bb28567e201b35aa",
  "challenge_type": "obfuscated_text_lock",
  "prompt": "gl1tch//llm-cap-v1::d2\nfrag@f8 // D3c0d3 the driFted Br13f ANd 4N5w3r tHrOUgH Payload.answer 0NLY\nfrag@d8 %% d3CK: slOt5 v10l37 cIndEr\nfrag@f6 %% d3ck: sloT2 4Mb3R h4Rb0r\nfrag@c9 || task: 0rD3R thE kept 5h4Rd WOrdS By 5l07 numBer fr0m loW to h1gh\nfrag@b3 %% dEcK: slOt3 C0b4L7 sabLe\nfrag@d3 %% AnswEr ruLe: R37urn ThE 5H4rd W0rd5 in UpPercaSe aScii J01N3D WIth hYpheNs\nfrag@e2 || d3Ck: SLot4 4mb3R 51gn4L\nfrag@e5 ^^ tasK: keEp onLy ShArds cArrying the 4MB3r TAg\nfrag@e4 :: d3CK: slot1 4mB3r 3Mb3R\nreply via payload.answer only // structured-json",
  "issued_at": "2026-03-07T02:58:20.639623+00:00",
  "expires_at": "2026-03-07T03:00:20.639623+00:00",
  "version": "1",
  "data": {
    "difficulty": 2,
    "profile": "llm_capability_v2",
    "response_contract": {
      "payload.answer": "UPPERCASE ASCII words joined with hyphens",
      "payload.decoded_preview": "optional free-form notes"
    }
  }
}
```

  </div>
  <div class="sample-card">
    <div class="sample-label">Agent response</div>

```json
{
  "challenge_id": "bb28567e201b35aa",
  "challenge_type": "obfuscated_text_lock",
  "payload": {
    "answer": "EMBER-HARBOR-SIGNAL",
    "decoded_preview": "kept amber shards ordered by slot"
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
    "answer": "EMBER-HARBOR-SIGNAL",
    "template_id": "amber_sort",
    "difficulty": 2
  }
}
```

## Why it fits LLM-capable clients

<div class="reason-grid">
  <div class="reason">
    <h3>Obfuscated</h3>
    <p>The key instruction is noisy, shuffled, and distorted instead of being directly machine-labeled.</p>
  </div>
  <div class="reason">
    <h3>Exact</h3>
    <p>The final answer is still deterministic: uppercase ASCII, hyphen-joined, exact expected value.</p>
  </div>
  <div class="reason">
    <h3>Verifiable</h3>
    <p>The server keeps the private verification copy and returns clear failure reasons instead of fuzzy scores.</p>
  </div>
</div>

## Built-in families

<div class="tile-grid">
  <div class="tile">
    <h3>obfuscated_text_lock</h3>
    <p>Primary challenge family for external LLM clients, with stronger obfuscated prompt patterns.</p>
  </div>
  <div class="tile">
    <h3>multi_pass_lock</h3>
    <p>Harder LLM family that layers filtering, transforms, and ordering into one prompt.</p>
  </div>
  <div class="tile">
    <h3>proof_of_work</h3>
    <p>Deterministic compute baseline with a bundled reference solver.</p>
  </div>
  <div class="tile">
    <h3>semantic_math_lock</h3>
    <p>Readable exact-constraint baseline that stays easy to inspect locally.</p>
  </div>
</div>

## Benchmarking

Use the built-in harness to compare weak non-LLM baselines against generated LLM-family
challenges:

```bash
agentproof benchmark obfuscated_text_lock --iterations 25 --difficulty 2 --template amber_sort
```

It reports per-solver attempts, solves, and success rate so you can see how often brittle parsers
still succeed against the current prompt family.

## What it is not

!!! warning

    `agentproof` is not provider attestation or identity proof.
    It is an LLM-capability CAPTCHA library.

## Continue

- Start with [Getting Started](getting-started.md)
- Compare built-in [Challenge Types](concepts.md)
- Open runnable [Examples](examples.md)
