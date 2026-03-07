# Changelog

## 0.2.1 - 2026-03-07

- Made `obfuscated_text_lock` fail gracefully when verifying from a public-only challenge payload
- Removed the demo server fallback that trusted client-supplied challenge objects during verification
- Added regression tests for public challenge verification and demo challenge-ID enforcement

## 0.2.0 - 2026-03-07

- Repositioned `agentproof` as an LLM-capability CAPTCHA library
- Added `obfuscated_text_lock` as the primary challenge family
- Added private server-side verification data via `Challenge.to_internal_dict()`
- Added a public/private CLI generation flow for obfuscated challenges
- Updated the local demo for manual LLM response entry and server-side challenge storage
- Rewrote the README and docs around the obfuscated public challenge flow

## 0.1.1 - 2026-03-06

- Fixed GitHub release creation workflow by checking out the repository before invoking `gh release`
- Polished README, repository metadata, issue templates, and demo project
- Added an automated integration test for the local demo app

## 0.1.0 - 2026-03-06

- Initial release candidate for the `agentproof` library
- Published distribution name is `agentproof-ai`
- Added `proof_of_work` and `semantic_math_lock` challenge families
- Added CLI, tests, docs, and GitHub workflows
