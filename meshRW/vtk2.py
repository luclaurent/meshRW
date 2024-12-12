"""
This class is a part of the meshRW library and will write a vtk file from a mesh using libvtk
----
Luc Laurent - luc.laurent@lecnam.net -- 2024
"""

import vtk

class fem2vtk():
    
    def __init__(self,nodes,elems,
                    nodalFields=None,
                    cellFields=None, 
                    filename=None,
                    opts={'binary':False}):
        # points
        points = vtk.vtkPoints()
        for i in range(len(nodes)):
            points.InsertNextPoint(nodes[i,:])
        # cells
        ugrid = vtk.vtkUnstructuredGrid()
        ugrid.SetPoints(points)
        #
        for k,v in elems.items():
            if k == 'tri3':
                nbnodes = 3            
                cell = vtk.vtkTriangle()
            elif k == 'tri6':
                nbnodes = 6
                cell = vtk.vtkQuadraticTriangle()
            elif k == 'quad4':
                nbnodes = 4
                cell = vtk.vtkQuad()
            elif k == 'quad8':
                nbnodes = 8
                cell = vtk.vtkQuadraticQuad()
            elif k == 'tet4':
                nbnodes = 4
                cell = vtk.vtkTetra()
            elif k == 'hex8':
                nbnodes = 8
                cell = vtk.vtkHexahedron()
            elif k =='tet10':
                nbnodes = 10
                cell = vtk.vtkQuadraticTetra()
            for t in v:            
                for i in range(nbnodes):
                    cell.GetPointIds().SetId(i,t[i])
                ugrid.InsertNextCell(cell.GetCellType(),cell.GetPointIds())
        # initialize polydata    
        if nodalFields:
            for k,v in nodalFields.items():
                nf = vtk.vtkDoubleArray()
                nf.SetName(k)
                if len(v.shape) == 1:
                    dim = 1
                else:
                    dim = v.shape[1]
                nf.SetNumberOfComponents(dim)
                for i,c in enumerate(v):
                    if dim == 1:
                        nf.InsertNextValue(c)
                    else:
                        nf.InsertNextTuple3(*c)
                ugrid.GetPointData().AddArray(nf)
        if cellFields:
            for k,v in cellFields.items():
                cf = vtk.vtkDoubleArray()
                cf.SetName(k)
                cf.SetNumberOfComponents(v.shape[1])
                for i,c in enumerate(v):
                    cf.InsertNextTuple3(*c)
                ugrid.GetCellData().AddArray(cf)
                
        # output
        if filename:
            writer = vtk.vtkXMLUnstructuredGridWriter()
            writer.SetFileName(filename)
            writer.SetInputDataObject(ugrid)
            if opts.get('binary',False):
                writer.SetFileType(vtk.VTK_BINARY)
            writer.Write()
        return ugrid