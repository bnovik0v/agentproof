# agentproof demo

This folder contains a small local web demo for the `agentproof` library. It uses only the Python
standard library for the server and imports the local package source directly, so you can run it
from VSCode without installing a separate web framework.

## What it shows

- public challenge generation
- server-side storage of the private verification copy
- manual response entry for `obfuscated_text_lock` and `multi_pass_lock`
- built-in solver behavior for the baseline families
- deterministic verification and failure modes

## Run it

From the repository root:

```bash
uv run python demo/app.py
```

Then open:

```text
http://127.0.0.1:8765
```

## Demo flow

1. Generate a challenge
2. If it is `obfuscated_text_lock` or `multi_pass_lock`, paste a response from an LLM-capable client
3. If it is a baseline family, use the built-in solver button
4. Verify the response
5. Edit the response JSON and verify again to trigger a deterministic failure

## Notes

- `obfuscated_text_lock` is the default view because it is the primary product path
- `multi_pass_lock` is available when you want a harder multi-step language challenge
- `proof_of_work` and `semantic_math_lock` stay useful for fast baseline checks
- the demo keeps internal challenge state in memory only; restart the server to clear it
