# Challenge Types

`agentproof` ships one primary LLM-capability challenge family and two baseline families.

## `obfuscated_text_lock`

Use this when you want the challenge itself to depend on recovering intent from obfuscated text.

What the client does:

- reads a noisy, shuffled instruction prompt
- recovers the rule hidden in the text
- returns a structured JSON payload with an exact answer

What the server verifies:

- challenge ID matches
- response is not expired
- `payload.answer` exists and matches the required format
- the normalized answer equals the private expected answer

Built-in templates:

- `amber_sort`
- `echo_reverse`
- `vowel_count`

Typical use cases:

- LLM-capability CAPTCHA experiments
- challenge-response gates for LLM-first APIs
- testing whether clients can recover intent from obfuscated text

Important constraint:

- there is intentionally no bundled solver for this family
- the challenge must be solved by an external LLM-capable client

## `proof_of_work`

Use this when you want a deterministic compute task with no language recovery component.

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

- deterministic smoke tests
- cheap baseline friction
- CLI and CI examples

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

- local demos
- readable examples
- deterministic constraint checks without obfuscation

## Determinism matters

`agentproof` intentionally avoids fuzzy verification.

Each built-in challenge is designed so the server can produce a clear yes/no result and, when it
fails, a concrete failure reason such as:

- `challenge_expired`
- `missing_answer`
- `invalid_answer_format`
- `answer_mismatch`
- `hash_mismatch`
- `wrong_word_count`
- `required_word_constraint_failed`
- `initial_sum_mismatch`

## Extending the library

Challenge families implement a shared internal protocol:

- generate
- solve
- verify

For challenge families that should only be solved by an external client, `solve(...)` can raise
`SolverUnavailableError`.
