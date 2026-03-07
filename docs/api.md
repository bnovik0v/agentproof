# API

## Public imports

```python
from agentproof import generate_challenge, solve_challenge, verify_response
from agentproof import ChallengeSpec, Challenge, AgentResponse, VerificationResult
from agentproof import SolverUnavailableError
```

## `ChallengeSpec`

Used to request a challenge.

Fields:

- `challenge_type`
- `ttl_seconds`
- `difficulty`
- `options`

Example:

```python
spec = ChallengeSpec(
    challenge_type="obfuscated_text_lock",
    difficulty=2,
    ttl_seconds=90,
    options={"template": "amber_sort"},
)
```

## `Challenge`

Represents an issued challenge payload.

Important fields:

- `challenge_id`
- `challenge_type`
- `prompt`
- `issued_at`
- `expires_at`
- `data`
- `version`

Important methods:

- `challenge.to_dict()`
  Safe public JSON without private verification data.
- `challenge.to_internal_dict()`
  Server-side JSON including `private_data` for later verification.

## `AgentResponse`

Represents the response returned by a client or reference solver.

Important fields:

- `challenge_id`
- `challenge_type`
- `payload`

## `VerificationResult`

Returned by `verify_response(...)`.

Fields:

- `ok`
- `reason`
- `details`

Common success value:

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

Common failure values:

- `challenge_id_mismatch`
- `challenge_type_mismatch`
- `challenge_expired`
- `missing_answer`
- `invalid_answer_format`
- `answer_mismatch`
- `missing_nonce`
- `missing_hash`
- `hash_mismatch`
- `insufficient_difficulty`
- `missing_text`
- `wrong_word_count`
- `required_word_constraint_failed`
- `initial_sum_mismatch`

## Solver availability

`solve_challenge(...)` works for:

- `proof_of_work`
- `semantic_math_lock`

`solve_challenge(...)` raises `SolverUnavailableError` for:

- `obfuscated_text_lock`
