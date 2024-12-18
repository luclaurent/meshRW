# meshRW

![GitHub](https://img.shields.io/github/license/luclaurent/meshRW?style=flat-square) [![pypi release](https://img.shields.io/pypi/v/meshrw.svg)](https://pypi.org/project/meshrw/) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14514790.svg)](https://doi.org/10.5281/zenodo.14514790) ![CI-pytest](https://github.com/luclaurent/meshRW/actions/workflows/CI-pytest.yml/badge.svg) ![code coverage](https://raw.githubusercontent.com/luclaurent/meshRW/refs/heads/coverage-badge/coverage.svg)

<!-- ![GitHub release (latest by date)](https://img.shields.io/github/v/release/luclaurent/meshRW?style=flat-square) ![GitHub all releases](https://img.shields.io/github/downloads/luclaurent/meshRW/total?style=flat-square)  -->

`meshRW` is a Python module that proposes basic readers and writers for `msh` ([gmsh](http://gmsh.info)) and `vtk/vtu/pvd` ([Paraview](https://www.paraview.org/)). It proposes:

* to read basic legacy `gmsh` mesh files (version: 2.2)
* to write mesh files including time series fields to any version of `gmsh` mesh files and legacy (`.vtk`) and XML (`.vtu`, with `.pvd`) VTK mesh file compatible with [Paraview](https://www.paraview.org/).


## Installation

Installation via `pip install meshRW`

## Usage

### Examples of usage

Examples of usage could be found in tests files: [`test_msh.py`](meshRW/tests/test_msh.py) and [`test_vtk.py`](meshRW/tests/test_vtk.py). 

### Read mesh files

`meshRW` can read `msh` files only. Notice that no field can be read.

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


### Write mesh files

`meshRW` can write `msh` and `vtk` files. Basic static and **time dependent** nodal and elemental fields can be written aswell.

The common syntax for writers is the following

        from meshRW import XXXX

            XXXX.zzzzWriter(
                filename = <name of the file>,
                nodes = <array of nodes coordinates>,
                title = <title of the file> (optional),
                elements = [
                    {
                        'connectivity': <name of the file>,
                        'type': <type (string) of elements (TRI3, TET4...)>,
                        'physgrp': <list/array of physical groups>,
                    },...
                ],
                fields = [
                    {
                        'data': <array of data>,
                        'type': <type of data ('nodal' or 'elemental')>,
                        'dim': <ndimension of data's array>,
                        'name': <name of the field>,
                    },            
                    {
                        'data': <array of data>,
                        'type': <name of the file>,
                        'dim': <dimension of data's array>,
                        'name': <name of the field>,
                        'nbsteps': <number of steps (transient field for instance)>,
                        'steps': <list of steps (time steps for instance)>
                        },...
                ],  
                opts = {...} (dictionary of specific options)
            )

* For `msh` format (based on [Legacy format, version 2.2](http://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format-version-2-_0028Legacy_0029) only with class `msh` and all meshes format provided by `gmsh` using class `msh2`):

    * for classical legacy file (not use the gmsh's libAPI) could be accessed by choosing `XXXX = msh` and `zzzz=msh` (`msh.mshWriter(...)`)
    * for any kind of  legacy file (not use the gmsh's libAPI) could be accessed by choosing `XXXX = msh2` and `zzzz=msh` (`msh2.mshWriter(...)`)
  
**NB:** 
* `filename` must contain `.msh` extension
* `opts` could be (for `msh2` only) `{'version': VV}` (`VV` could be equal to `2, 2.2, 4, 4.1` that corresponds to `gmsh` mesh files version - `MshFileVersion`) 
* in the case of time series data, all the fields are given by default in the output file (to obtain one field per file, pass option `append = True` to the writer).

* for `vtk` format ([only non-binary legacy](https://kitware.github.io/vtk-examples/site/VTKFileFormats/))

    * for classical legacy file (not use the VTK library) could be accessed by choosing `XXXX = vtk` and `zzzz=vtk` (`vtk.vtkWriter(...)`)
    * for any kind of  legacy file (not use the gmsh's libAPI) could be accessed by choosing `XXXX = vtk2` and `zzzz=vtk` (`vtk2.vtkWriter(...)`)
  
**NB:** 
* `filename` must contain `.vtk`, `.vtu` (recommanded) extension
* `opts` could be (for `vtk2` only) `{'binary': True/False, 'ascii': True/False}` (these options force data format in `.vtu` files) 
* in the case of time series fields, the fields are written separated series files with the following format : `basename.NNN.vtu` (NNN correspond the number of the step starting at 0). In this case, a [Paraview](https://www.paraview.org/Wiki/ParaView/Data_formats#PVD_File_Format) `.pvd` file is also generated to declare all the steps and associated mesh files with the time step values.

            

<!-- ## Examples
### Example: load and display a mesh file from msh

### Example: add a static nodal field to an existing mesh

### Example: add a time-dependent nodal field to an exisiting mesh -->

## References

Developments are based on [GMSH API documentation](https://gmsh.info/doc/texinfo/gmsh.html#Gmsh-API), [GMSH tutorials](https://gitlab.onelab.info/gmsh/gmsh/-/tree/master/tutorials/python?ref_type=heads), [VTK documentation](https://vtk.org/doc/nightly/html/index.html), [Kitware blog posts](https://www.kitware.com/blog/), [VTK discourse](https://discourse.vtk.org/).


## Other similar tools

* [`meshio`](https://github.com/nschloe/meshio)

## LICENSE



Copyright 2024 luc.laurent@lecnam.net

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
