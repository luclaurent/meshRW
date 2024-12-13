""""
This file includes the definition
and tools to manipulate MSH format
Documentation available here:
https://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format
----
Luc Laurent - luc.laurent@lecnam.net -- 2021

"""
from loguru import logger as Logger


def loadElementDict():
    """
    dictionary from element (string) to msh element number
    """
    elementDict = {
        # 2-nodes line
        'LIN2': {'code':1, 'nodes':2, 'dim':1},
        # 3-nodes second order line
        'LIN3': {'code': 8, 'nodes':3, 'dim':1},
        # 4-nodes third order line
        'LIN4': None,
        # 3-nodes triangle
        'TRI3': {'code': 2, 'nodes':3, 'dim':2},
        # 6-nodes second order triangle (3 vertices, 3 on edges)
        'TRI6': {'code': 9, 'nodes':6, 'dim':2},
        # 9-nodes cubic order triangle (3 vertices, 3 on edges and 3 inside)
        'TRI9': None,
        # 10-nodes higher order triangle (3 vertices, 6 on edges and 1 inside)
        'TRI10': None,
        # 12-nodes higher order triangle (3 vertices and 9 on edges)
        'TRI12': None,
        # 15-nodes higher order triangle (3 vertices, 9 on edges and 3 inside)
        'TRI15': None,
        # 4-nodes quadrangle
        'QUA4': {'code': 3, 'nodes':4, 'dim':2},
        # 8-nodes second order quadrangle (4 vertices and 4 on edges)
        'QUA8': {'code': 16, 'nodes':8, 'dim':2},
        # 9-nodes higher order quadrangle (4 vertices, 4 on edges and 1 inside)
        'QUA9': {'code': 10, 'nodes':9, 'dim':2},
        # 4-nodes tetrahedron
        'TET4': {'code': 4, 'nodes':4, 'dim':3},
        # 10-nodes second order tetrahedron (4 vertices and 6 on edges)
        'TET10': {'code': 11, 'nodes':10, 'dim':3},
        # 8-nodes hexahedron
        'HEX8': {'code': 5, 'nodes':8, 'dim':3},
        # 20-nodes second order hexahedron (8 vertices and 12 on edges)
        'HEX20': {'code': 17, 'nodes':20, 'dim':3},
        # 27-nodes higher order hexahedron
        # (8 vertices, 12 on edges, 6 on faces and 1 inside)
        'HEX27': {'code': 12, 'nodes':27, 'dim':3},
        # 6-nodes prism
        'PRI6': {'code': 6, 'nodes':6, 'dim':3},
        # 15-nodes second order prism (6 vertices and 9 on edges)
        'PRI15': {'code': 18, 'nodes':15, 'dim':3},
        # 18-nodes higher order prism (6 vertices, 9 on edges and 3 on faces)
        'PRI18': {'code': 13, 'nodes':18, 'dim':3},
        # 5-node pyramid
        'PYR5': {'code': 7, 'nodes':5, 'dim':3},
        # 13-nodes second order pyramid (5 edges and 8 on edges)
        'PYR13': {'code': 19, 'nodes':13, 'dim':3},
        # 14-nodes higher order pyramid (5 edges, 8 on edges and 1 inside)
        'PYR14': {'code': 14, 'nodes':14, 'dim':3},
        # 1-node point
        'NOD1': {'code': 15, 'nodes':1, 'dim':0},
    }
    return elementDict


def getMSHElemType(txtEltype):
    """
    Get the element type defined as in gmsh (refer to gmsh documentation for numbering) from text declaration
    syntax:
        getMshElemType(txtEltype)

    input:
        txtEltype: element declared using string (if number is used the function will return it)
    output:
        element type defined as gmsh number
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


def getElemTypeFromMSH(elementNum):
    """
    Get the element type from id (integer) defined in gmsh (refer to gmsh documentation for numbering)
    syntax:
        getElemTypeFromMSH(elementNum)

    input:
        elementNum: integer used in gmsh to declare element
    output:
        global name of the element
    """
    # load the dictionary
    elementDict = loadElementDict()
    globalName = None
    # get the name of the element using the integer iD along the dictionary
    for k,v in elementDict.items():
        if v:
            if v.get('code', None) == elementNum:
                globalName = k
                break
    # if the name of the element if not available show error
    if globalName is None:
        Logger.error(f'Element type not found with id {elementNum}')
    return globalName


def getNumberNodes(txtElemtype):
    """
    Get the number of nodes for a specific element type type (declare as string)
        syntax:
            getNumberNodes(txtElemtype)

       input:
            txtElemtype: element declared using string (if number is used the function wil return it)
        output:
            number of nodes for txtEltype
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


def getNumberNodesFromNum(elementNum):
    """
    Get the number of nodfs for a specific element type type (declare as string)
        syntax:
            getNumberNodesFromNum(elementNum)

        input:
            elementNum: integer used in gmsh to declare element
        output:
            number of nodes for txtEltype
    """
    return getNumberNodes(getElemTypeFromMSH(elementNum))


# Keywords MSH
DFLT_FILE_OPEN_CLOSE = {'open': '$MeshFormat',
                        'close': '$EndMeshFormat'}
DFLT_FILE_VERSION = '2.2 0 8'
DFLT_NODES_OPEN_CLOSE = {'open': '$Nodes',
                         'close': '$EndNodes'}
DFLT_ELEMS_OPEN_CLOSE = {'open': '$Elements',
                         'close': '$EndElements'}
DFLT_FIELDS_NODES_OPEN_CLOSE = {'open': '$NodeData',
                                'close': '$EndNodeData'}
DFLT_FIELDS_ELEMS_OPEN_CLOSE = {'open': '$ElementData',
                                'close': '$EndElementData'}
