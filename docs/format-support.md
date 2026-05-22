# Format support

## Gmsh (`.msh`)

### Reader

- Supported: legacy MSH 2.2 geometry/connectivity.
- Not supported: field import.

### Writer

- `meshRW.msh`: legacy writer.
- `meshRW.msh2`: uses Gmsh API and can target additional MSH versions via options.

## VTK (`.vtk`, `.vtu`, `.pvd`)

### Legacy VTK

- `meshRW.vtk` writes ASCII legacy `.vtk` output.

### XML VTK

- `meshRW.vtk2` writes `.vtu` and transient `.pvd` index files.
- For transient fields, per-step files are emitted with numbered suffixes.

## Known constraints

- Input/output dictionaries must include consistent dimensions and entity counts.
- Some advanced cell/field combinations depend on the backend (`vtk` vs `vtk2`).
- Large transient exports can generate many files; plan output folder organization accordingly.
