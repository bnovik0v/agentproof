# Concepts

## Challenge families

`agentproof` currently ships two built-in challenge families:

- `proof_of_work`
- `semantic_math_lock`

Each family supports:

- generation
- solving with the reference implementation
- verification

## Determinism

Verification logic should be machine-checkable and stable. The library avoids fuzzy scoring.

## Extensibility

Challenge families implement a shared protocol, which keeps custom handlers isolated from the public API.

