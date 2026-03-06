# Contributing

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs]"
```

## Quality checks

```bash
ruff check .
ruff format .
mypy .
pytest
python -m build
```

## Pull requests

- Keep the public API typed and documented
- Add tests for every behavior change
- Update docs and changelog for user-facing changes
- Prefer deterministic verification logic over heuristic checks

