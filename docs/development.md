# Development

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,docs]
```

## Run tests

```bash
pytest meshRW/tests -q
```

## Lint

```bash
ruff check meshRW
```

## Build docs

```bash
sphinx-build -W --keep-going -b html docs docs/_build/html
```

## Build package

```bash
hatch build
```

## CI workflows

- `CI-pytest.yml`: matrix tests, lint, and coverage artifact.
- `CI-docs.yml`: strict documentation build check.
- `CI-publish.yml`: build/sign/release and publish to package indexes.
