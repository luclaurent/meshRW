""""
This file includes the definition and tools to manipulate MSH format
Documentation available here: https://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format
----
Luc Laurent - luc.laurent@lecnam.net -- 2021

"""


def loadElementDict():
    """
    dictionary from element (string) to VTK number
    """
    elementDict = {
        # 2-nodes line
        'LIN2': 3,
        # 3-nodes second order line
        'LIN3': 21,
        # 4-nodes third order line
        'LIN4': None,
        # 3-nodes triangle
        'TRI3': 5,
        # 6-nodes second order triangle (3 vertices, 3 on edges)
        'TRI6': 22,
        # 9-nodes cubic order triangle (3 vertices, 3 on edges and 3 inside)
        'TRI9': None,
        # 10-nodes higher order triangle (3 vertices, 6 on edges and 1 inside)
        'TRI10': None,
        # 12-nodes higher order triangle (3 vertices and 9 on edges)
        'TRI12': None,
        # 15-nodes higher order triangle (3 vertices, 9 on edges and 3 inside)
        'TRI15': None,
        # 4-nodes quadrangle
        'QUA4': 9,
        # 8-nodes second order quadrangle (4 vertices and 4 on edges)
        'QUA8': 23,
        # 9-nodes higher order quadrangle (4 vertices, 4 on edges and 1 inside)
        'QUA9': None,
        # 4-nodes tetrahedron
        'TET4': 10,
        # 10-nodes second order tetrahedron (4 vertices and 6 on edges)
        'TET10': 24,
        # 8-nodes hexahedron
        'HEX8': 12,
        # 20-nodes second order hexahedron (8 vertices and 12 on edges)
        'HEX20': 25,
        # 27-nodes higher order hexahedron (8 vertices, 
        # 12 on edges, 6 on faces and 1 inside)
        'HEX27': None,
        # 6-nodes prism
        'PRI6': 13,
        # 15-nodes second order prism (6 vertices and 9 on edges)
        'PRI15': None,
        # 18-nodes higher order prism (6 vertices, 9 on edges and 3 on faces)
        'PRI18': None,
        # 5-node pyramid
        'PYR5': 14,
        # 13-nodes second order pyramid (5 edges and 8 on edges)
        'PYR13': None,
        # 14-nodes higher order pyramid (5 edges, 8 on edges and 1 inside)
        'PYR14': None,
        # 1-node point
        'NOD1': 1,
        #
        # many nodes
        'NODN': 2,
        # many lines (poly-lines)
        'LINEN': 4,
        # many stripped triangles
        'TRIN': 6,
        # polygons
        'POLY': 7,
        # pixel
        'PIXEL': 8,
        # voxel
        'VOXEL': 11
    }
    return elementDict


def loadNodesElement():
    """
        dictionary of number of nodes per element type
    """
    numPerElementDict = {
        # 2-nodes line
        'LIN2': 2,
        # 3-nodes second order line
        'LIN3': 3,
        # 4-nodes third order line
        'LIN4': None,
        # 3-nodes triangle
        'TRI3': 3,
        # 6-nodes second order triangle (3 vertices, 3 on edges)
        'TRI6': 6,
        # 9-nodes cubic order triangle (3 vertices, 3 on edges and 3 inside)
        'TRI9': None,
        # 10-nodes higher order triangle (3 vertices, 6 on edges and 1 inside)
        'TRI10': None,
        # 12-nodes higher order triangle (3 vertices and 9 on edges)
        'TRI12': None,
        # 15-nodes higher order triangle (3 vertices, 9 on edges and 3 inside)
        'TRI15': None,
        # 4-nodes quadrangle
        'QUA4': 4,
        # 8-nodes second order quadrangle (4 vertices and 4 on edges)
        'QUA8': 8,
        # 9-nodes higher order quadrangle (4 vertices, 4 on edges and 1 inside)
        'QUA9': None,
        # 4-nodes tetrahedron
        'TET4': 4,
        # 10-nodes second order tetrahedron (4 vertices and 6 on edges)
        'TET10': 10,
        # 8-nodes hexahedron
        'HEX8': 8,
        # 20-nodes second order hexahedron (8 vertices and 12 on edges)
        'HEX20': 20,
        # 27-nodes higher order hexahedron (8 vertices,
        # 12 on edges, 6 on faces and 1 inside)
        'HEX27': None,
        # 6-nodes prism
        'PRI6': 6,
        # 15-nodes second order prism (6 vertices and 9 on edges)
        'PRI15': None,
        # 18-nodes higher order prism (6 vertices, 9 on edges and 3 on faces)
        'PRI18': None,
        # 5-node pyramid
        'PYR5': 5,
        # 13-nodes second order pyramid (5 edges and 8 on edges)
        'PYR13': None,
        # 14-nodes higher order pyramid (5 edges, 8 on edges and 1 inside)
        'PYR14': None,
        # 1-node point
        'NOD1': 1,
        #
        # many nodes
        'NODN': -1,
        # many lines (poly-lines)
        'LINEN': -1,
        # many stripped triangles
        'TRIN': -1,
        # polygons
        'POLY': -1,
        # pixel
        'PIXEL': 4,
        # voxel
        'VOXEL': 8
    }
    return numPerElementDict


def getVTKtoElem():
    """
        dictionary from VTK element to name of element (string)
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
        'VTK_VOXEL': 'VOXEL'
    }
    return VTKtoElem


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
DFLT_ELEMS_TYPE = 'CELLS_TYPES'
DFLT_ELEMS_DATA = 'CELL_DATA'
DFLT_FIELD = 'FIELD'
DFLT_SCALARS = 'SCALARS'
DFLT_TABLE = 'LOOKUP_TABLE'
DFLT_TABLE_DEFAULT = 'default'
