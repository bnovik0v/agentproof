# API

## Public imports

```python
from agentproof import generate_challenge, solve_challenge, verify_response
from agentproof import ChallengeSpec, Challenge, AgentResponse, VerificationResult
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
    challenge_type="semantic_math_lock",
    ttl_seconds=90,
    options={"topic": "security", "word_count": 7},
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
    "nonce": "223",
    "hash": "00bf9b61..."
  }
}
```

Common failure values:

- `challenge_id_mismatch`
- `challenge_type_mismatch`
- `challenge_expired`
- `missing_nonce`
- `missing_hash`
- `hash_mismatch`
- `insufficient_difficulty`
- `missing_text`
- `wrong_word_count`
- `required_word_constraint_failed`
- `initial_sum_mismatch`

