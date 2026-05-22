# meshRW

![GitHub](https://img.shields.io/github/license/luclaurent/meshRW?style=flat-square)
[![PyPI release](https://img.shields.io/pypi/v/meshrw.svg)](https://pypi.org/project/meshrw/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14514789.svg)](https://doi.org/10.5281/zenodo.14514789)
![CI tests](https://github.com/luclaurent/meshRW/actions/workflows/CI-pytest.yml/badge.svg)
![code coverage](https://raw.githubusercontent.com/luclaurent/meshRW/refs/heads/coverage-badge/coverage.svg)

meshRW is a lightweight Python library to read/write mesh files for Gmsh and VTK-based workflows.

## What it provides

- Read legacy Gmsh meshes (`.msh`, v2.2).
- Write Gmsh meshes (`.msh`) with static or transient fields.
- Write legacy VTK (`.vtk`) and XML VTK (`.vtu` + `.pvd`) outputs.
- Export nodal and elemental data, including time-series results.

## Installation

```bash
pip install meshRW
```

For contributors (lint + docs tooling):

```bash
pip install -e .[dev,docs]
```

## Quick start

### Read a Gmsh mesh

```python
from meshRW import msh

mesh = msh.mshReader(filename="input.msh", dim=3)
nodes = mesh.getNodes()
elements = mesh.getElements(dictFormat=True)
```

### Write a VTK/VTU result

```python
from meshRW import vtk2

vtk2.vtkWriter(
    filename="output.vtu",
    nodes=nodes,
    elements=elements,
    fields=[],
)
```

## Writer input model

All writers follow the same data structure:

- `nodes`: array-like `(n_nodes, 2|3)`.
- `elements`: list of dictionaries with `connectivity`, `type`, optional `physgrp`.
- `fields`: list of dictionaries with `name`, `type` (`nodal`/`elemental`), `dim`, `data`, and optional time metadata (`nbsteps`, `steps`).

## Format notes

- `.msh`: use `meshRW.msh` (legacy) or `meshRW.msh2` (Gmsh API-backed, version options).
- `.vtk`: use `meshRW.vtk` (legacy writer).
- `.vtu` / `.pvd`: use `meshRW.vtk2` for XML and transient outputs.

## Documentation

- Project docs index: [docs/index.md](docs/index.md)
- Getting started: [docs/getting-started.md](docs/getting-started.md)
- API overview: [docs/api-overview.md](docs/api-overview.md)
- Format support: [docs/format-support.md](docs/format-support.md)
- Development guide: [docs/development.md](docs/development.md)

## Development and quality

- Tests: `pytest meshRW/tests -q`
- Lint: `ruff check meshRW`
- Docs build: `sphinx-build -W --keep-going -b html docs docs/_build/html`

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

## Related projects

- [meshio](https://github.com/nschloe/meshio)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
