import pickle
from pathlib import Path

import numpy

from meshRW import vtk, vtk2

# load current path
CurrentPath = Path(__file__).parent
DataPath = CurrentPath / Path('test_data')
# data file for testing
datafile = DataPath / Path('debug.h5')
# artifacts directory
ArtifactsPath = CurrentPath / Path('artifacts')
ArtifactsPath.mkdir(exist_ok=True)


def test_VTKwriterTemporal():
    # open data
    hf = open(datafile, 'rb')
    data = pickle.load(hf)
    hf.close()
    # extract nodes list
    nodes = data['n']
    # extract elements list and data
    elemsData = data['e']
    # generate data on nodes
    dataNodes = numpy.random.rand(nodes.shape[0], nodes.shape[1])
    # generate data on elements
    dataElem = numpy.random.rand(elemsData['TET4'].shape[0] + elemsData['PRI6'].shape[0], 2)
    # generate steps
    dataElemStep = [numpy.random.rand(elemsData['TET4'].shape[0] + elemsData['PRI6'].shape[0], 3) for i in range(5)]
    # write msh file
    outputfile = ArtifactsPath / Path('build-temp.vtk')
    vtk.vtkWriter(
        filename=outputfile,
        nodes=nodes,
        elements=[
            {
                'connectivity': elemsData[list(elemsData.keys())[0]] - 1,
                'type': list(elemsData.keys())[0],
                'physgrp': [5, 5],
            },
            {
                'connectivity': elemsData[list(elemsData.keys())[1]] - 1,
                'type': list(elemsData.keys())[1],
                'physgrp': [6, 6],
            },
        ],
        fields=[
            {
                'data': dataNodes,
                'type': 'nodal',
                'dim': 3,
                'name': 'nodal3',
            },  # ,'steps':list of steps,'nbsteps':number of steps],
            {'data': dataElem, 'type': 'elemental', 'dim': 2, 'name': 'name_2'},
            {'data': dataElemStep, 'type': 'elemental', 'dim': 3, 'name': 'alongsteps', 'nbsteps': 5},
        ],  # ,'steps':list of steps,'nbsteps':number of steps]
    )
    for i in range(5):
        artifact = outputfile.parent / Path(outputfile.stem + f'.{i:d}' + '.vtk')
        assert artifact.exists()



def test_VTKwriterNoPhysGrp():
    # open data
    hf = open(datafile, 'rb')
    data = pickle.load(hf)
    hf.close()
    # extract nodes list
    nodes = data['n']
    # extract elements list and data
    elemsData = data['e']
    # generate data on nodes
    dataNodes = numpy.random.rand(nodes.shape[0], nodes.shape[1])
    # generate data on elements
    dataElem = numpy.random.rand(elemsData['TET4'].shape[0] + elemsData['PRI6'].shape[0], 2)
    # write msh file
    outputfile = ArtifactsPath / Path('build.vtk')
    vtk.vtkWriter(
        filename=outputfile,
        nodes=nodes,
        elements=[
            {
                'connectivity': elemsData[list(elemsData.keys())[0]] - 1,
                'type': list(elemsData.keys())[0]
            },
            {
                'connectivity': elemsData[list(elemsData.keys())[1]] - 1,
                'type': list(elemsData.keys())[1]
            },
        ]
    )
    assert outputfile.exists()

def test_VTKwriterStatic():
    # open data
    hf = open(datafile, 'rb')
    data = pickle.load(hf)
    hf.close()
    # extract nodes list
    nodes = data['n']
    # extract elements list and data
    elemsData = data['e']
    # generate data on nodes
    dataNodes = numpy.random.rand(nodes.shape[0], nodes.shape[1])
    # generate data on elements
    dataElem = numpy.random.rand(elemsData['TET4'].shape[0] + elemsData['PRI6'].shape[0], 2)
    # write msh file
    outputfile = ArtifactsPath / Path('build.vtk')
    vtk.vtkWriter(
        filename=outputfile,
        nodes=nodes,
        elements=[
            {
                'connectivity': elemsData[list(elemsData.keys())[0]] - 1,
                'type': list(elemsData.keys())[0],
                'physgrp': [5, 5],
            },
            {
                'connectivity': elemsData[list(elemsData.keys())[1]] - 1,
                'type': list(elemsData.keys())[1],
                'physgrp': [6, 6],
            },
        ],
        fields=[
            {
                'data': dataNodes,
                'type': 'nodal',
                'dim': 3,
                'name': 'nodal3',
            },  # ,'steps':list of steps,'nbsteps':number of steps],
            {'data': dataElem, 'type': 'elemental', 'dim': 2, 'name': 'name_2'},
        ],
    )
    assert outputfile.exists()


def test_VTK2writerTemporal():
    # open data
    hf = open(datafile, 'rb')
    data = pickle.load(hf)
    hf.close()
    # extract nodes list
    nodes = data['n']
    # extract elements list and data
    elemsData = data['e']
    # generate data on nodes
    dataNodes = numpy.random.rand(nodes.shape[0], nodes.shape[1])
    # generate data on elements
    dataElem = numpy.random.rand(elemsData['TET4'].shape[0] + elemsData['PRI6'].shape[0], 2)
    # generate steps
    dataElemStep = [numpy.random.rand(elemsData['TET4'].shape[0] + elemsData['PRI6'].shape[0], 3) for i in range(5)]
    # write msh file
    outputfile = ArtifactsPath / Path('build2-temp.vtu')
    extension = outputfile.suffix
    vtk2.vtkWriter(
        filename=outputfile,
        nodes=nodes,
        elements=[
            {
                'connectivity': elemsData[list(elemsData.keys())[0]] - 1,
                'type': list(elemsData.keys())[0],
                'physgrp': [5, 5],
            },
            {
                'connectivity': elemsData[list(elemsData.keys())[1]] - 1,
                'type': list(elemsData.keys())[1],
                'physgrp': [6, 6],
            },
        ],
        fields=[
            {
                'data': dataNodes,
                'type': 'nodal',
                'dim': 3,
                'name': 'nodal3',
            },  # ,'steps':list of steps,'nbsteps':number of steps],
            {'data': dataElem, 'type': 'elemental', 'dim': 2, 'name': 'name_2'},
            {
                'data': dataElemStep,
                'type': 'elemental',
                'dim': 3,
                'name': 'alongsteps',
                'nbsteps': 5,
            },  # ,'steps':list of steps,'nbsteps':number of steps]
        ],
    )
    for i in range(len(dataElemStep)):
        assert outputfile.with_suffix(f'.{i:d}' + extension).exists()
    assert outputfile.with_suffix('.pvd').exists()



def test_VTK2writerNoPhysGrp():
    # open data
    hf = open(datafile, 'rb')
    data = pickle.load(hf)
    hf.close()
    # extract nodes list
    nodes = data['n']
    # extract elements list and data
    elemsData = data['e']
    # generate data on nodes
    dataNodes = numpy.random.rand(nodes.shape[0], nodes.shape[1])
    # generate data on elements
    dataElem = numpy.random.rand(elemsData['TET4'].shape[0] + elemsData['PRI6'].shape[0], 2)
    # write msh file
    outputfile = ArtifactsPath / Path('build.vtk')
    vtk.vtkWriter(
        filename=outputfile,
        nodes=nodes,
        elements=
            {
                'connectivity': elemsData[list(elemsData.keys())[0]] - 1,
                'type': list(elemsData.keys())[0]
            }
        ,
        fields=[
            {
                'data': dataNodes,
                'type': 'nodal',
                'dim': 3,
                'name': 'nodal3',
            },  # ,'steps':list of steps,'nbsteps':number of steps],
            {'data': dataElem, 'type': 'elemental', 'dim': 2, 'name': 'name_2'},
        ]
    )
    assert outputfile.exists()

def test_VTK2writerStatic():
    # open data
    hf = open(datafile, 'rb')
    data = pickle.load(hf)
    hf.close()
    # extract nodes list
    nodes = data['n']
    # extract elements list and data
    elemsData = data['e']
    # generate data on nodes
    dataNodes = numpy.random.rand(nodes.shape[0], nodes.shape[1])
    # generate data on elements
    dataElem = numpy.random.rand(elemsData['TET4'].shape[0] + elemsData['PRI6'].shape[0], 2)
    # write msh file
    outputfile = ArtifactsPath / Path('build2.vtu')
    vtk2.vtkWriter(
        filename=outputfile,
        nodes=nodes,
        elements=[
            {
                'connectivity': elemsData[list(elemsData.keys())[0]] - 1,
                'type': list(elemsData.keys())[0],
                'physgrp': [5, 5],
            },
            {
                'connectivity': elemsData[list(elemsData.keys())[1]] - 1,
                'type': list(elemsData.keys())[1],
                'physgrp': [6, 6],
            },
        ],
        fields=[
            {
                'data': dataNodes,
                'type': 'nodal',
                'dim': 3,
                'name': 'nodal3',
            },  # ,'steps':list of steps,'nbsteps':number of steps],
            {'data': dataElem, 'type': 'elemental', 'dim': 2, 'name': 'name_2'},
        ],
    )

    assert outputfile.exists()
