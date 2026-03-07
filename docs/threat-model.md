# Threat Model

## What `agentproof` helps with

- adding a structured LLM-capability challenge before access to an API
- requiring clients to recover intent from obfuscated text
- enforcing machine-readable responses
- keeping private verification data on the server while exposing only the public challenge

## What it does not prove

`agentproof` does not prove:

- which model produced the response
- whether the caller is using a specific provider
- whether the caller used hardware-backed execution
- whether the caller is malicious but well-automated

## Correct way to think about it

`agentproof` answers:

> Can this client recover and execute an obfuscated instruction and return the exact expected
> result?

It does **not** answer:

> Is this definitely a trusted AI agent?

## Deployment advice

Use `agentproof` as one signal in a broader system. In production, combine it with:

- rate limiting
- application authentication
- server-side challenge storage or signed challenge state
- expiration checks
- replay protection
- logging and abuse monitoring

## Why the verification is strict

The library prefers exact constraints over fuzzy scoring so that:

- the server can explain failures clearly
- tests stay deterministic
- challenge behavior is stable across environments

## Why the public and private payload split matters

For the obfuscated family:

- the public challenge should travel to the client
- the private expected answer should not
- verification should happen against the original in-memory challenge or its internal JSON form
