# Contributing to meshRW

## Prerequisites

- Python 3.9+
- A virtual environment

## Setup

```bash
git clone https://github.com/luclaurent/meshRW.git
cd meshRW
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,docs]
```

## Development workflow

1. Create a feature branch from `main`.
2. Implement changes with tests and doc updates.
3. Run checks locally:

```bash
ruff check meshRW
pytest meshRW/tests -q
sphinx-build -W --keep-going -b html docs docs/_build/html
```

4. Open a pull request with a clear summary and rationale.

## Pull request checklist

- [ ] Code is tested.
- [ ] New behavior is documented.
- [ ] Public API changes include docstring updates.
- [ ] README/docs are updated when applicable.

## Reporting issues

Use GitHub Issues and include:

- meshRW version
- Python version
- Reproducible minimal example
- Full traceback/log
