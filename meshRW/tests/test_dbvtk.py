import pytest
from meshRW.dbvtk import (
    loadElementDict,
    getVTKtoElem,
    getVTKObj,
    getVTKElemType,
    getElemTypeFromVTK,
    getNumberNodes,
    getNumberNodesFromNum,
)

def test_loadElementDict():
    element_dict = loadElementDict()
    assert 'LIN2' in element_dict
    assert element_dict['LIN2']['code'] == 3
    assert element_dict['LIN2']['nodes'] == 2
    assert element_dict['LIN2']['dim'] == 1
    assert element_dict['LIN2']['vtkobj'] is not None

def test_getVTKtoElem():
    vtk_to_elem = getVTKtoElem()
    assert 'VTK_VERTEX' in vtk_to_elem
    assert vtk_to_elem['VTK_VERTEX'] == 'NOD1'

def test_getVTKObj():
    vtk_obj, num_nodes = getVTKObj('VTK_TRIANGLE')
    assert vtk_obj is not None
    assert num_nodes == 3

    vtk_obj, num_nodes = getVTKObj('VTK_QUADRATIC_EDGE')
    assert vtk_obj is not None
    assert num_nodes == 3

def test_getVTKElemType():
    elem_type, num_nodes = getVTKElemType('VTK_TRIANGLE')
    assert elem_type == 5
    assert num_nodes == 3

    elem_type, num_nodes = getVTKElemType(5)
    assert elem_type == 5
    assert num_nodes == -1

def test_getElemTypeFromVTK():
    elem_type = getElemTypeFromVTK(5)
    assert elem_type == 'TRI3'

    elem_type = getElemTypeFromVTK(12)
    assert elem_type == 'HEX8'

def test_getNumberNodes():
    num_nodes = getNumberNodes('TRI3')
    assert num_nodes == 3

    num_nodes = getNumberNodes('HEX8')
    assert num_nodes == 8

def test_getNumberNodesFromNum():
    num_nodes = getNumberNodesFromNum(5)
    assert num_nodes == 3

    num_nodes = getNumberNodesFromNum(12)
    assert num_nodes == 8
