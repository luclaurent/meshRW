# Getting started

## Install

```bash
pip install meshRW
```

For development and docs:

```bash
pip install -e .[dev,docs]
```

## Read a MSH file

```python
from meshRW import msh

mesh = msh.mshReader(filename="mesh.msh", dim=3)
nodes = mesh.getNodes()
elements = mesh.getElements(dictFormat=True)
```

## Write a legacy MSH file

```python
import numpy as np
from meshRW import msh

nodes = np.array([
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
])

elements = [
    {
        "connectivity": np.array([[1, 2, 3]]),
        "type": "TRI3",
        "physgrp": np.array([1]),
    }
]

msh.mshWriter(filename="example.msh", nodes=nodes, elements=elements, fields=[])
```

## Write VTU/PVD time series

```python
from meshRW import vtk2

vtk2.vtkWriter(
    filename="results.vtu",
    nodes=nodes,
    elements=elements,
    fields=[
        {
            "name": "temperature",
            "type": "nodal",
            "dim": 1,
            "data": [[100.0, 120.0, 110.0], [105.0, 125.0, 115.0]],
            "nbsteps": 2,
            "steps": [0.0, 1.0],
        }
    ],
)
```
