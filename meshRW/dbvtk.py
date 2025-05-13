""" 
This file is part of the meshRW package
---
This file includes the definition and tools to manipulate MSH format
Documentation available here: https://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format
----
Luc Laurent - luc.laurent@lecnam.net -- 2021

"""
from typing import Union
import vtk
from loguru import logger as Logger


def loadElementDict()-> dict:
    """
    Load a dictionary mapping element types to their corresponding VTK properties.

    This function returns a dictionary where the keys are element type strings 
    (e.g., 'LIN2', 'TRI3', 'HEX8') and the values are dictionaries containing 
    information about the element type, including its VTK code, number of nodes, 
    dimensionality, and associated VTK object.

    Returns:
        dict: A dictionary with the following structure:
            {
                'ELEMENT_TYPE': {
                    'code': int,          # VTK code for the element type
                    'nodes': int,         # Number of nodes in the element (-1 for variable)
                    'dim': int,           # Dimensionality of the element (0, 1, 2, or 3)
                    'vtkobj': vtkObject   # Corresponding VTK object
                },
                ...

    Notes:
        - Some element types are defined but have a value of `None`, indicating 
          that they are not yet implemented or supported.
        - The VTK objects (e.g., vtk.vtkLine, vtk.vtkTriangle) must be imported 
          from the VTK library for this function to work.
    """
    elementDict = {
        # 2-nodes line
        'LIN2': {'code': 3, 'nodes': 2, 'dim': 1, 'vtkobj': vtk.vtkLine()},
        # 3-nodes second order line
        'LIN3': {'code': 21, 'nodes': 3, 'dim': 1, 'vtkobj': vtk.vtkQuadraticEdge()},
        # 4-nodes third order line
        'LIN4': None,
        # 3-nodes triangle
        'TRI3': {'code': 5, 'nodes': 3, 'dim': 2, 'vtkobj': vtk.vtkTriangle()},
        # 6-nodes second order triangle (3 vertices, 3 on edges)
        'TRI6': {'code': 22, 'nodes': 6, 'dim': 2, 'vtkobj': vtk.vtkQuadraticTriangle()},
        # 9-nodes cubic order triangle (3 vertices, 3 on edges and 3 inside)
        'TRI9': None,
        # 10-nodes higher order triangle (3 vertices, 6 on edges and 1 inside)
        'TRI10': None,
        # 12-nodes higher order triangle (3 vertices and 9 on edges)
        'TRI12': None,
        # 15-nodes higher order triangle (3 vertices, 9 on edges and 3 inside)
        'TRI15': None,
        # 4-nodes quadrangle
        'QUA4': {'code': 9, 'nodes': 4, 'dim': 2, 'vtkobj': vtk.vtkQuad()},
        # 8-nodes second order quadrangle (4 vertices and 4 on edges)
        'QUA8': {'code': 23, 'nodes': 8, 'dim': 2, 'vtkobj': vtk.vtkQuadraticQuad()},
        # 9-nodes higher order quadrangle (4 vertices, 4 on edges and 1 inside)
        'QUA9': None,
        # 4-nodes tetrahedron
        'TET4': {'code': 10, 'nodes': 4, 'dim': 3, 'vtkobj': vtk.vtkTetra()},
        # 10-nodes second order tetrahedron (4 vertices and 6 on edges)
        'TET10': {'code': 24, 'nodes': 10, 'dim': 3, 'vtkobj': vtk.vtkQuadraticTetra()},
        # 8-nodes hexahedron
        'HEX8': {'code': 12, 'nodes': 8, 'dim': 3, 'vtkobj': vtk.vtkHexahedron()},
        # 20-nodes second order hexahedron (8 vertices and 12 on edges)
        'HEX20': {'code': 25, 'nodes': 20, 'dim': 3, 'vtkobj': vtk.vtkQuadraticHexahedron()},
        # 27-nodes higher order hexahedron (8 vertices,
        # 12 on edges, 6 on faces and 1 inside)
        'HEX27': None,
        # 6-nodes prism
        'PRI6': {'code': 13, 'nodes': 6, 'dim': 3, 'vtkobj': vtk.vtkWedge()},
        # 15-nodes second order prism (6 vertices and 9 on edges)
        'PRI15': None,
        # 18-nodes higher order prism (6 vertices, 9 on edges and 3 on faces)
        'PRI18': None,
        # 5-node pyramid
        'PYR5': {'code': 14, 'nodes': 5, 'dim': 3, 'vtkobj': vtk.vtkPyramid()},
        # 13-nodes second order pyramid (5 edges and 8 on edges)
        'PYR13': None,
        # 14-nodes higher order pyramid (5 edges, 8 on edges and 1 inside)
        'PYR14': None,
        # 1-node point
        'NOD1': {'code': 1, 'nodes': 1, 'dim': 0, 'vtkobj': vtk.vtkVertex()},
        #
        # many nodes
        'NODN': {'code': 2, 'nodes': -1, 'dim': 0, 'vtkobj': vtk.vtkPolyVertex()},
        # many lines (poly-lines)
        'LINEN': {'code': 4, 'nodes': -1, 'dim': 1, 'vtkobj': vtk.vtkPolyLine()},
        # many stripped triangles
        'TRIN': {'code': 6, 'nodes': -1, 'dim': 2, 'vtkobj': vtk.vtkTriangleStrip()},
        # polygons
        'POLY': {'code': 7, 'nodes': -1, 'dim': 2, 'vtkobj': vtk.vtkPolygon()},
        # pixel
        'PIXEL': {'code': 8, 'nodes': -1, 'dim': 2, 'vtkobj': vtk.vtkPixel()},
        # voxel
        'VOXEL': {'code': 11, 'nodes': -1, 'dim': 3, 'vtkobj': vtk.vtkVoxel()},
    }
    return elementDict


def getVTKtoElem()-> dict:
    """
    Returns a dictionary mapping VTK element types to their corresponding 
    element type codes used in another system.

    The mapping includes standard VTK element types, quadratic elements, 
    and some special cases like polygons and voxel types.

    Returns:
        dict: A dictionary where the keys are VTK element type strings 
                (e.g., 'VTK_VERTEX', 'VTK_TRIANGLE') and the values are 
                corresponding element type codes (e.g., 'NOD1', 'TRI3').
    """

    VTKtoElem = {
        'VTK_VERTEX': 'NOD1',
        'VTK_LINE': 'LIN2',
        'VTK_TRIANGLE': 'TRI3',
        'VTK_QUAD': 'QUAD4',
        'VTK_TETRA': 'TET4',
        'VTK_HEXAHEDRON': 'HEX8',
        'VTK_WEDGE': 'PRI6',
        'VTK_PYRAMID': 'PYR5',
        'VTK_QUADRATIC_EDGE': 'LIN3',
        'VTK_QUADRATIC_TRIANGLE': 'TRI6',
        'VTK_QUADRATIC_QUAD': 'QUA8',
        'VTK_QUADRATIC_TETRA': 'TET10',
        'VTK_QUADRATIC_HEXAHEDRON': 'HEX20',
        #
        'VTK_POLY_VERTEX': 'NODN',
        'VTK_POLY_LINE': 'LINEN',
        'VTK_TRIANGLE_STRIP': 'TRIN',
        'VTK_POLYGON': 'POLY',
        'VTK_PIXEL': 'PIXEL',
        'VTK_VOXEL': 'VOXEL',
    }
    return VTKtoElem


def getVTKObj(txtEltype):
    """
    Get the vtk class from libvtk from text declaration
    syntax:
        getVTKEObjType(txtEltype)

    input:
        txtEltype: element declared using VTK string (if number is used the function wil return it)
    output:
        vtk class for the requested element
        number of nodes on element
    """

    VTKtoElem = getVTKtoElem()
    elementDict = loadElementDict()

    # depending on the type of txtEltype
    numPerElement = -1
    if txtEltype.upper() in VTKtoElem.keys():
        txtEltype = VTKtoElem[txtEltype]
    vtkobj = elementDict[txtEltype.upper()].get('vtkobj', None)
    numPerElement = getNumberNodes(txtEltype.upper())
    if not vtkobj:
        Logger.error(f'Element type {txtEltype} not implemented')
    return vtkobj, numPerElement


def getVTKElemType(txtEltype: Union[str, int])-> tuple:
    """
    Get the VTK element type and the number of nodes per element.

    This function retrieves the VTK element type number and the number of nodes per element 
    based on the provided text declaration or integer. The VTK element type number corresponds 
    to the numbering defined in the VTK documentation.

    Args:
        txtEltype (Union[str, int]): The element type, either as a string (VTK string declaration) 
                                     or as an integer (VTK element type number).

    Returns:
        tuple: A tuple containing:
            - elementNum (int): The VTK element type number.
            - numPerElement (int): The number of nodes per element. Returns -1 if not applicable.

    Raises:
        Logger.error: If the provided element type is not implemented or invalid.

    Note:
        - If a string is provided, it is converted to the corresponding VTK element type number.
        - If an integer is provided, it is returned directly as the element type number.
        - Refer to the VTK documentation for the numbering and details of element types.
    """

    VTKtoElem = getVTKtoElem()
    elementDict = loadElementDict()

    # depending on the type of txtEltype
    numPerElement = -1
    if isinstance(txtEltype, int):
        elementNum = txtEltype
    else:
        if txtEltype.upper() in VTKtoElem.keys():
            txtEltype = VTKtoElem[txtEltype]
        elementNum = elementDict[txtEltype.upper()].get('code', None)
        numPerElement = getNumberNodes(txtEltype.upper())
    if not elementNum:
        Logger.error(f'Element type {txtEltype} not implemented')
    return elementNum, numPerElement


def getElemTypeFromVTK(elementNum: int) -> str:
    """
    Get the global name of an element type based on its numerical ID as defined in Gmsh.

    This function retrieves the element type name corresponding to the given numerical ID
    by searching through a dictionary of element definitions. The dictionary is loaded
    using the `loadElementDict` function. If the ID is not found, an error is logged.

    Args:
        elementNum (int): The numerical ID of the element type as defined in Gmsh.

    Returns:
        str: The global name of the element type if found, otherwise `None`.

    Raises:
        Logs an error if the element type ID is not found in the dictionary.
    """
    # load the dictionary
    elementDict = loadElementDict()
    globalName = None
    # get the name of the element using the integer iD along the dictionary
    for k, v in elementDict.items():
        if v:
            if v.get('code', None) == elementNum:
                globalName = k
                break
    # if the name of the element if not available show error
    if globalName is None:
        Logger.error(f'Element type not found with id {elementNum}')
    return globalName


def getNumberNodes(txtElemtype: str) -> int:
    """
    Get the number of nodes for a specific element type.

    Args:
        txtElemtype (str): The element type as a string. If a number is used, 
                           the function will return it.

    Returns:
        int: The number of nodes for the specified element type, or None if 
             the element type is not defined.

    Raises:
        Logs an error if the specified element type does not exist in the 
        element dictionary.

    Notes:
        The function relies on `loadElementDict()` to retrieve the dictionary 
        of element types and their properties.
    """

    elementDict = loadElementDict()
    # check if the type of element exists
    if txtElemtype in elementDict.keys():
        # get the number of nodes for the type of element
        if elementDict[txtElemtype]:
            nbNodes = elementDict[txtElemtype].get('nodes', None)
    else:
        # show error message if the type of element does not exist
        Logger.error(f'Element type {txtElemtype} not defined')
    return nbNodes


def getNumberNodesFromNum(elementNum: int) -> int:
    """
    Get the number of nodes for a specific element type based on its numerical identifier.

    This function determines the number of nodes associated with a given element type
    by first converting the numerical identifier to its corresponding element type
    and then retrieving the number of nodes for that element type.

    Args:
        elementNum (int): The numerical identifier of the element type as used in Gmsh.

    Returns:
        int: The number of nodes associated with the specified element type.
    """

    return getNumberNodes(getElemTypeFromVTK(elementNum))


# DEFAULT VALUES
ALLOWED_EXTENSIONS = [
    '.vtk',
    '.vtk.bz2',
    '.vtk.gz',
    '.vtu',
    '.vtu.bz2',
    '.vtu.gz',
]


# Keywords MSH
DFLT_HEADER_VERSION = '# vtk DataFile Version 2.0'
DFLT_TYPE_ASCII = 'ASCII'
DFLT_FILE_VERSION = '2.2 0 8'
DFLT_TYPE_MESH = 'DATASET UNSTRUCTURED_GRID'
DFLT_NODES = 'POINTS'
DFLT_NODES_DATA = 'POINT_DATA'
DFLT_DOUBLE = 'double'
DFLT_FLOAT = 'float'
DFLT_INT = 'int'
DFLT_ELEMS = 'CELLS'
DFLT_ELEMS_TYPE = 'CELL_TYPES'
DFLT_ELEMS_DATA = 'CELL_DATA'
DFLT_FIELD = 'FIELD'
DFLT_SCALARS = 'SCALARS'
DFLT_TABLE = 'LOOKUP_TABLE'
DFLT_TABLE_DEFAULT = 'default'
