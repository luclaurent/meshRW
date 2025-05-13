"""
This file is part of the meshRW package
---
This file includes the definition
and tools to manipulate MSH format
Documentation available here:
https://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format
----
Luc Laurent - luc.laurent@lecnam.net -- 2021

"""
from typing import Union
from loguru import logger as Logger


def loadElementDict()-> dict:
    """
    Load a dictionary mapping element types to their corresponding properties.

    This function returns a dictionary where the keys are element type strings 
    (e.g., 'LIN2', 'TRI3', 'HEX8') and the values are dictionaries containing 
    the following properties of the element:
    - 'code': The numerical code representing the element type.
    - 'nodes': The number of nodes associated with the element.
    - 'dim': The spatial dimension of the element.

    Some element types may have a value of `None`, indicating that their 
    properties are not defined.

    Returns:
        dict: A dictionary mapping element type strings to their properties.
    """
    
    elementDict = {
        # 2-nodes line
        'LIN2': {'code': 1, 'nodes': 2, 'dim': 1},
        # 3-nodes second order line
        'LIN3': {'code': 8, 'nodes': 3, 'dim': 1},
        # 4-nodes third order line
        'LIN4': None,
        # 3-nodes triangle
        'TRI3': {'code': 2, 'nodes': 3, 'dim': 2},
        # 6-nodes second order triangle (3 vertices, 3 on edges)
        'TRI6': {'code': 9, 'nodes': 6, 'dim': 2},
        # 9-nodes cubic order triangle (3 vertices, 3 on edges and 3 inside)
        'TRI9': None,
        # 10-nodes higher order triangle (3 vertices, 6 on edges and 1 inside)
        'TRI10': None,
        # 12-nodes higher order triangle (3 vertices and 9 on edges)
        'TRI12': None,
        # 15-nodes higher order triangle (3 vertices, 9 on edges and 3 inside)
        'TRI15': None,
        # 4-nodes quadrangle
        'QUA4': {'code': 3, 'nodes': 4, 'dim': 2},
        # 8-nodes second order quadrangle (4 vertices and 4 on edges)
        'QUA8': {'code': 16, 'nodes': 8, 'dim': 2},
        # 9-nodes higher order quadrangle (4 vertices, 4 on edges and 1 inside)
        'QUA9': {'code': 10, 'nodes': 9, 'dim': 2},
        # 4-nodes tetrahedron
        'TET4': {'code': 4, 'nodes': 4, 'dim': 3},
        # 10-nodes second order tetrahedron (4 vertices and 6 on edges)
        'TET10': {'code': 11, 'nodes': 10, 'dim': 3},
        # 8-nodes hexahedron
        'HEX8': {'code': 5, 'nodes': 8, 'dim': 3},
        # 20-nodes second order hexahedron (8 vertices and 12 on edges)
        'HEX20': {'code': 17, 'nodes': 20, 'dim': 3},
        # 27-nodes higher order hexahedron
        # (8 vertices, 12 on edges, 6 on faces and 1 inside)
        'HEX27': {'code': 12, 'nodes': 27, 'dim': 3},
        # 6-nodes prism
        'PRI6': {'code': 6, 'nodes': 6, 'dim': 3},
        # 15-nodes second order prism (6 vertices and 9 on edges)
        'PRI15': {'code': 18, 'nodes': 15, 'dim': 3},
        # 18-nodes higher order prism (6 vertices, 9 on edges and 3 on faces)
        'PRI18': {'code': 13, 'nodes': 18, 'dim': 3},
        # 5-node pyramid
        'PYR5': {'code': 7, 'nodes': 5, 'dim': 3},
        # 13-nodes second order pyramid (5 edges and 8 on edges)
        'PYR13': {'code': 19, 'nodes': 13, 'dim': 3},
        # 14-nodes higher order pyramid (5 edges, 8 on edges and 1 inside)
        'PYR14': {'code': 14, 'nodes': 14, 'dim': 3},
        # 1-node point
        'NOD1': {'code': 15, 'nodes': 1, 'dim': 0},
    }
    return elementDict


def getMSHElemType(txtEltype: Union[str, int])-> int:
    """
    Get the Gmsh element type number from a textual declaration or return the number directly if provided.

    This function retrieves the element type number as defined in the Gmsh documentation. If the input is a string, 
    it looks up the corresponding number in a predefined dictionary. If the input is already an integer, it simply 
    returns the input value.

    Args:
        txtEltype (Union[str, int]): The element type, either as a string (e.g., "triangle", "quad") or as an integer.

    Returns:
        int: The Gmsh element type number corresponding to the input.

    Raises:
        KeyError: If the string input does not match any known element type in the dictionary.
        ValueError: If the input is invalid or the element type is not implemented.

    Note:
        Refer to the Gmsh documentation for the numbering scheme of element types.
    """
    elementDict = loadElementDict()

    # depending on the type of txtEltype
    # - if int: return txtEltype
    # - else get the number from the dictionary
    if isinstance(txtEltype, int):
        elementNum = txtEltype
    else:
        elementNum = elementDict[txtEltype.upper()].get('code', None)
    # show error if the type is not available
    if not elementNum:
        Logger.error(f'Element type {txtEltype} not implemented')
    return elementNum


def getElemTypeFromMSH(elementNum: int) -> str:
    """
    Get the global name of an element type based on its numerical ID as defined in Gmsh.

    This function retrieves the element type name corresponding to the given numerical ID 
    from a dictionary of element types. The dictionary is loaded using the `loadElementDict` 
    function. If the ID is not found, an error is logged.

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

    This function retrieves the number of nodes associated with a given element type 
    from a predefined dictionary. The element type is provided as a string.

    Args:
        txtElemtype (str): The element type as a string. If a number is used, 
                           the function will return it.

    Returns:
        int: The number of nodes for the specified element type. Returns 0 if the 
             element type is not found or if the dictionary does not contain 
             the 'nodes' key for the given type.

    Raises:
        Logs an error message if the specified element type is not defined in the dictionary.
    """
    # load the dictionary
    elementDict = loadElementDict()
    nbNodes = 0
    # check if the type of element exists
    if txtElemtype in elementDict.keys():
        # get the number of nodes for the type of element
        if elementDict[txtElemtype]:
            nbNodes = elementDict[txtElemtype].get('nodes', None)
    else:
        # show error message if the type of element does not exist
        Logger.error(f'Element type {txtElemtype} not defined')
    return nbNodes

def getDim(txtElemtype: str) -> int:
    """    
    Get the spatial dimension for a specific element type.

    This function retrieves the spatial dimension associated with a given element type,
    which is specified as a string. If the element type is not found in the dictionary,
    an error message is logged.

    Args:
        txtElemtype (str): The element type specified as a string.

    Returns:
        int: The spatial dimension of the element type, or 0 if the element type is not found.

    Raises:
        None: This function does not raise exceptions but logs an error if the element type is undefined.
    """
    # load the dictionary
    elementDict = loadElementDict()
    nbNodes = 0
    # check if the type of element exists
    if txtElemtype in elementDict.keys():
        # get the number of nodes for the type of element
        if elementDict[txtElemtype]:
            nbNodes = elementDict[txtElemtype].get('dim', None)
    else:
        # show error message if the type of element does not exist
        Logger.error(f'Element type {txtElemtype} not defined')
    return nbNodes


def getNumberNodesFromNum(elementNum: int) -> int:
    """
    Get the number of nodes for a specific element type based on its numerical identifier.

    This function determines the number of nodes associated with a given element type
    in Gmsh by first retrieving the element type as a string and then mapping it to
    the corresponding number of nodes.

    Args:
        elementNum (int): The numerical identifier of the element type in Gmsh.

    Returns:
        int: The number of nodes associated with the specified element type.
    """
    return getNumberNodes(getElemTypeFromMSH(elementNum))


# DEFAULT VALUES
ALLOWED_EXTENSIONS = ['.msh', '.msh.bz2', '.msh.gz']

# Keywords MSH
DFLT_FILE_OPEN_CLOSE = {'open': '$MeshFormat', 'close': '$EndMeshFormat'}
DFLT_FILE_VERSION = '2.2 0 8'
DFLT_NODES_OPEN_CLOSE = {'open': '$Nodes', 'close': '$EndNodes'}
DFLT_ELEMS_OPEN_CLOSE = {'open': '$Elements', 'close': '$EndElements'}
DFLT_FIELDS_NODES_OPEN_CLOSE = {'open': '$NodeData', 'close': '$EndNodeData'}
DFLT_FIELDS_ELEMS_OPEN_CLOSE = {'open': '$ElementData', 'close': '$EndElementData'}
