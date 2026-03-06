# API

## Public entry points

```python
from agentproof import generate_challenge, solve_challenge, verify_response
from agentproof import ChallengeSpec, Challenge, AgentResponse, VerificationResult
```

## ChallengeSpec

- `challenge_type`
- `ttl_seconds`
- `difficulty`
- `options`

## VerificationResult

- `ok`
- `reason`
- `details`

