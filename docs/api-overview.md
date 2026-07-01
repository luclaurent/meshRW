# API overview

## Core modules

- `meshRW.msh`: legacy Gmsh v2.2 writer and reader (`mshWriter`, `mshReader`).
- `meshRW.msh2`: Gmsh API-backed writer for multiple MSH versions.
- `meshRW.vtk`: legacy VTK (`.vtk`) writer.
- `meshRW.vtk2`: VTK library-backed writer for `.vtk` and `.vtu`/`.pvd`.

## Shared infrastructure

- `meshRW.writerclass`: canonical abstract base class and shared analysis helpers.
- `meshRW.writerClass`: compatibility alias to `meshRW.writerclass`.
- `meshRW.fileio`: safe file handling wrapper.
- `meshRW.dbmsh` and `meshRW.dbvtk`: element/type lookup dictionaries.
- `meshRW.various`: utility helpers.

## Compatibility policy

- Snake_case APIs are canonical for current releases.
- Legacy camelCase entry points remain available for backward compatibility.
- Legacy module names `configMESH` and `writerClass` are preserved as import shims.

## Data model expectations

### Nodes

2D array-like structure with shape `(n_nodes, 2|3)`.

### Elements

List of dictionaries with at least:

- `connectivity`: array-like connectivity table.
- `type`: element type (string or numeric id depending on context).
- `physgrp` (optional): physical group id(s).

### Fields

List of dictionaries with:

- `name`: field name.
- `type`: `nodal` or `elemental`.
- `dim`: scalar/vector size.
- `data`: array-like values.
- `nbsteps`, `steps` (optional): for transient fields.

## Error handling

Writers perform structural checks and raise `ValueError` or generic `Exception` in invalid states (e.g., unsupported extension, incompatible shapes).
