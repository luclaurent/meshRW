# meshRW documentation

meshRW provides lightweight mesh readers and writers focused on:

- Legacy Gmsh MSH (reader + writer)
- VTK legacy files and VTK XML (`.vtu` + `.pvd`) writers
- Static and transient nodal/elemental field export

## Why meshRW

meshRW is designed for workflows where you need transparent file-level control over mesh and field exports without bringing a full simulation framework.

## Documentation map

- [Getting Started](getting-started.md): installation and first examples.
- [API Overview](api-overview.md): main modules and responsibilities.
- [Format Support](format-support.md): supported formats and limitations.
- [Development](development.md): local quality checks, tests, and doc build.

```{toctree}
:maxdepth: 2
:caption: Contents

getting-started
api-overview
format-support
development
```

## Project links

- Repository: <https://github.com/luclaurent/meshRW>
- Package: <https://pypi.org/project/meshrw/>
- Issues: <https://github.com/luclaurent/meshRW/issues>
