# Challenge Types

`agentproof` currently ships two built-in challenge families.

## `proof_of_work`

Use this when you want a deterministic compute task with no natural-language component.

What the agent does:

- reads the payload
- searches for a nonce
- returns a nonce and hash pair

What the server verifies:

- challenge ID matches
- response is not expired
- hash recomputes correctly
- hash satisfies the required difficulty

Typical use cases:

- cheap anti-abuse friction
- deterministic smoke tests
- baseline challenge-response verification

## `semantic_math_lock`

Use this when you want a readable challenge that still has exact measurable constraints.

What the agent does:

- reads required words and word-count rules
- produces text that matches all constraints
- returns the text in structured JSON

What the server verifies:

- challenge ID matches
- response is not expired
- exact word count
- required words appear exactly once
- initial-letter ASCII sum matches the target

Typical use cases:

- reverse-CAPTCHA experiments
- structured agent behavior checks
- demos where human-readable prompts matter

## Determinism matters

`agentproof` intentionally avoids fuzzy verification.

Each built-in challenge is designed so the server can produce a clear yes/no result and, when it
fails, a concrete failure reason such as:

- `challenge_expired`
- `hash_mismatch`
- `wrong_word_count`
- `required_word_constraint_failed`
- `initial_sum_mismatch`

## Extending the library

Challenge families implement a shared internal protocol:

- generate
- solve
- verify

That keeps custom challenge logic isolated from the public API while preserving a consistent
library interface.

