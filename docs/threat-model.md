# Threat Model

## What `agentproof` helps with

- adding structured challenge-response verification to an API
- making low-effort manual interaction less convenient
- requiring machine-readable responses
- enforcing expirations and replay resistance when your application stores challenge IDs

## What it does not prove

`agentproof` does not prove:

- which model produced the response
- whether the caller is using a specific provider
- whether the caller used hardware-backed execution
- whether the caller is malicious but well-automated

## Correct way to think about it

`agentproof` answers:

> Can this client complete a deterministic, agent-oriented challenge?

It does **not** answer:

> Is this definitely a trusted AI agent?

## Deployment advice

Use `agentproof` as one signal in a broader system. In production, combine it with:

- rate limiting
- application authentication
- server-side challenge storage
- expiration checks
- replay protection
- logging and abuse monitoring

## Why the verification is strict

The library prefers exact constraints over fuzzy scoring so that:

- the server can explain failures clearly
- tests stay deterministic
- challenge behavior is stable across environments

