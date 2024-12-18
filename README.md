# meshRW

![GitHub](https://img.shields.io/github/license/luclaurent/meshRW?style=flat-square) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/luclaurent/meshRW?style=flat-square) ![GitHub all releases](https://img.shields.io/github/downloads/luclaurent/meshRW/total?style=flat-square) ![CI-pytest](https://github.com/luclaurent/meshRW/workflows/CI-pytest/badge.svg)

`meshRW` is a Python module that proposes basic readers and writers for `msh` ([gmsh](http://gmsh.info)) and `vtk/vtu/pvd` ([Paraview](https://www.paraview.org/)). It proposes:


## Installation

Installation via `pip install .`
## Usage

### Read mesh files

`meshRW` can read `msh` files. Notice that no field can be read.

* For `msh` format ([only Legacy version 2](http://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format-version-2-_0028Legacy_0029)):

    * Read the file

            from meshRW import msh
            dataMesh = msh.mshReader(filename=<name of the file>, dim=<2 or 3>)

        Argument `dim` (which is optional) could be switched to the value `2` in order to force to extract nodes coordinates in 2D (z-axis coordinate will be removed).

    * Get coordinates of the nodes
     
             nodes = dataMesh.getNodes()

    * Get the list of tags number 

             tags = dataMesh.getTags() 

    * Get the list of types of elements
     
             tags = dataMesh.getTypes() 

    * Get the list of elements
 
             elements = dataMesh.getElements(type=<types of elements>, tag=<tags>, dictFormat=<True or False>)
        
        The `getElements` property 


## Write mesh files

`meshRW` can write `msh` and `vtk` files. Basic static and **time dependent** nodal and elemental fields can be written aswell.

* For `msh` format (based on [Legacy format, version 2.2](http://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format-version-2-_0028Legacy_0029) only with class `msh` and all meshes format provided by `gmsh` using class `msh2`):


* for `vtk` format ([only non-binary legacy](https://kitware.github.io/vtk-examples/site/VTKFileFormats/))

        from meshRW import vtk
        dataMesh = vtk.vtkWriter(filename=<name of the file>, dim=<2 or 3>)

## Examples
### Example: load and display a mesh file from msh

### Example: add a static nodal field to an existing mesh

### Example: add a time-dependent nodal field to an exisiting mesh

## Other similar tools

* [`meshio`](https://github.com/nschloe/meshio)

MSH read : 

    from meshRW import msh
    data = msh.mshReader(filename=)

VTK/MSH write: see on `test.py`