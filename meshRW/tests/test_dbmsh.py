import pytest

from meshRW.dbmsh import (
    loadElementDict,
    getMSHElemType,
    getElemTypeFromMSH,
    getNumberNodes,
    getDim,
    getNumberNodesFromNum,
)

def test_loadElementDict():
    element_dict = loadElementDict()
    assert isinstance(element_dict, dict)
    assert 'LIN2' in element_dict
    assert element_dict['LIN2'] == {'code': 1, 'nodes': 2, 'dim': 1}
    assert element_dict['LIN4'] is None

def test_getMSHElemType():
    assert getMSHElemType('LIN2') == 1
    assert getMSHElemType('TRI3') == 2
    assert getMSHElemType(5) == 5
    with pytest.raises(KeyError):
        getMSHElemType('INVALID')

def test_getElemTypeFromMSH():
    assert getElemTypeFromMSH(1) == 'LIN2'
    assert getElemTypeFromMSH(2) == 'TRI3'
    assert getElemTypeFromMSH(5) == 'HEX8'
    assert getElemTypeFromMSH(15) == 'NOD1'
    assert getElemTypeFromMSH(999) is None  # Logs an error

def test_getNumberNodes():
    assert getNumberNodes('LIN2') == 2
    assert getNumberNodes('TRI3') == 3
    assert getNumberNodes('HEX8') == 8
    assert getNumberNodes('LIN4') == 0  # Undefined element
    assert getNumberNodes('INVALID') == 0  # Logs an error

def test_getDim():
    assert getDim('LIN2') == 1
    assert getDim('TRI3') == 2
    assert getDim('HEX8') == 3
    assert getDim('LIN4') == 0  # Undefined element
    assert getDim('INVALID') == 0  # Logs an error

def test_getNumberNodesFromNum():
    assert getNumberNodesFromNum(1) == 2
    assert getNumberNodesFromNum(2) == 3
    assert getNumberNodesFromNum(5) == 8
    assert getNumberNodesFromNum(999) == 0  # Logs an error