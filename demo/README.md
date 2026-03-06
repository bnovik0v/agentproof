# agentproof demo

This folder contains a small local web demo for the `agentproof` library. It uses only the
Python standard library for the server and imports the local package source directly, so you can
run it from VSCode without installing a separate web framework.

## What it shows

- challenge generation
- reference solver output
- response verification
- easy manual tampering to inspect failure modes

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
2. Auto-solve it with the bundled solver
3. Verify the response
4. Edit the response JSON and verify again to trigger a deterministic failure

## Notes

- `proof_of_work` difficulty `16` is a good default for local demos
- `semantic_math_lock` is easier to inspect manually because the constraints are readable
- the demo does not persist state; everything is driven by the JSON payloads shown on screen

