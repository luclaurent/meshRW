""""
This file includes the definition and tools to manipulate MSH format
Documentation available here: https://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format
----
Luc Laurent - luc.laurent@lecnam.net -- 2021

"""


def loadElementDict():
    """
    dictionary from element (string) to msh element number
    """
    elementDict = {
        # 2-nodes line
        'LIN2': 1,
        # 3-nodes second order line
        'LIN3': 8,
        # 4-nodes third order line
        'LIN4': None,
        # 3-nodes triangle
        'TRI3': 2,
        # 6-nodes second order triangle (3 vertices, 3 on edges)
        'TRI6': 9,
        # 9-nodes cubic order triangle (3 vertices, 3 on edges and 3 inside)
        'TRI9': None,
        # 10-nodes higher order triangle (3 vertices, 6 on edges and 1 inside)
        'TRI10': None,
        # 12-nodes higher order triangle (3 vertices and 9 on edges)
        'TRI12': None,
        # 15-nodes higher order triangle (3 vertices, 9 on edges and 3 inside)
        'TRI15': None,
        # 4-nodes quadrangle
        'QUA4': 3,
        # 8-nodes second order quadrangle (4 vertices and 4 on edges)
        'QUA8': 16,
        # 9-nodes higher order quadrangle (4 vertices, 4 on edges and 1 inside)
        'QUA9': 10,
        # 4-nodes tetrahedron
        'TET4': 4,
        # 10-nodes second order tetrahedron (4 vertices and 6 on edges)
        'TET10': 11,
        # 8-nodes hexahedron
        'HEX8': 5,
        # 20-nodes second order hexahedron (8 vertices and 12 on edges)
        'HEX20': 17,
        # 27-nodes higher order hexahedron (8 vertices, 12 on edges, 6 on faces and 1 inside)
        'HEX27': 12,
        # 6-nodes prism
        'PRI6': 6,
        # 15-nodes second order prism (6 vertices and 9 on edges)
        'PRI15': 18,
        # 18-nodes higher order prism (6 vertices, 9 on edges and 3 on faces)
        'PRI18': 13,
        # 5-node pyramid
        'PYR5': 7,
        # 13-nodes second order pyramid (5 edges and 8 on edges)
        'PYR13': 19,
        # 14-nodes higher order pyramid (5 edges, 8 on edges and 1 inside)
        'PYR14': 14,
        # 1-node point
        'NOD1': 15
    }
    return elementDict


def loadNodesElement():
    """
        dictionary of number of nodes per element type
    """
    elementDict = {
        # 2-nodes line
        'LIN2': 2,
        # 3-nodes second order line
        'LIN3': 3,
        # 4-nodes third order line
        'LIN4': 4,
        # 3-nodes triangle
        'TRI3': 3,
        # 6-nodes second order triangle (3 vertices, 3 on edges)
        'TRI6': 6,
        # 9-nodes cubic order triangle (3 vertices, 3 on edges and 3 inside)
        'TRI9': 9,
        # 10-nodes higher order triangle (3 vertices, 6 on edges and 1 inside)
        'TRI10': 10,
        # 12-nodes higher order triangle (3 vertices and 9 on edges)
        'TRI12': 12,
        # 15-nodes higher order triangle (3 vertices, 9 on edges and 3 inside)
        'TRI15': 15,
        # 4-nodes quadrangle
        'QUA4': 4,
        # 8-nodes second order quadrangle (4 vertices and 4 on edges)
        'QUA8': 8,
        # 9-nodes higher order quadrangle (4 vertices, 4 on edges and 1 inside)
        'QUA9': 9,
        # 4-nodes tetrahedron
        'TET4': 4,
        # 10-nodes second order tetrahedron (4 vertices and 6 on edges)
        'TET10': 10,
        # 8-nodes hexahedron
        'HEX8': 8,
        # 20-nodes second order hexahedron (8 vertices and 12 on edges)
        'HEX20': 20,
        # 27-nodes higher order hexahedron (8 vertices, 12 on edges, 6 on faces and 1 inside)
        'HEX27': 27,
        # 6-nodes prism
        'PRI6': 6,
        # 15-nodes second order prism (6 vertices and 9 on edges)
        'PRI15': 15,
        # 18-nodes higher order prism (6 vertices, 9 on edges and 3 on faces)
        'PRI18': 18,
        # 5-node pyramid
        'PYR5': 5,
        # 13-nodes second order pyramid (5 edges and 8 on edges)
        'PYR13': 13,
        # 14-nodes higher order pyramid (5 edges, 8 on edges and 1 inside)
        'PYR14': 14,
        # 1-node point
        'NOD1': 1
    }
    return elementDict


#Keywords MSH
DFLT_FILE_OPEN_CLOSE={'open':'$MeshFormat','close':'$EndMeshFormat'}
DFLT_FILE_VERSION='2.2 0 8'
DFLT_NODES_OPEN_CLOSE={'open':'$Nodes','close':'$EndNodes'}
DFLT_ELEMS_OPEN_CLOSE={'open':'$Elements','close':'$EndElements'}
DFLT_FIELDS_NODES_OPEN_CLOSE={'open':'$NodesData','close':'$EndNodesData'}
DFLT_FIELDS_ELEMS_OPEN_CLOSE={'open':'$ElementData','close':'$EndElementData'}
