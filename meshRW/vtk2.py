"""
This class is a part of the meshRW library and will write a vtk file from a mesh using libvtk
----
Luc Laurent - luc.laurent@lecnam.net -- 2024
"""

from pathlib import Path
from typing import Union

import numpy as np
import vtk
import vtkmodules.util.numpy_support as ns
from loguru import logger as Logger
from lxml import etree

from . import configMESH, dbvtk, various, writerClass


class vtkWriter(writerClass.writer):
    def __init__(
        self,
        filename: Union[str, Path] = None,
        nodes: Union[list, np.ndarray] = None,
        elements: dict = None,
        fields: Union[list, np.ndarray] = None,
        append: bool = False,
        title: str = None,
        opts: dict = {'binary': False, 'ascii': True},
    ):
        #
        Logger.info('Start writing vtk/vtu file using libvtk')
        # prepare new fields (from physical groups for instance)
        newFields = self.createNewFields(elements)
        if newFields:
            if not fields:
                fields = list()
            fields.extend(newFields)
        # initialization
        super().__init__(filename, nodes, elements, fields, append, title, opts)
        # vtk data
        self.ugrid = None
        self.writer = None
        # load specific configuration
        self.db = dbvtk
        # write contents depending on the number of steps
        self.writeContentsSteps(nodes, elements, fields)

    def getAppend(self):
        """
        Obtain the append option
        """
        return self.append

    def setOptions(self, options: dict):
        """Default options"""
        self.binary = options.get('binary', False)
        self.ascii = options.get('ascii', False)

    def writeContentsSteps(self, nodes, elements, fields=None, numStep=None):
        """Write content along steps"""
        # create dictionary for preparing pvd file writing
        if self.nbSteps > 0:
            dataPVD = dict()
        # initialize data
        # create UnstructuredGrid
        self.ugrid = vtk.vtkUnstructuredGrid()
        # add points
        self.writeNodes(nodes)
        # elements
        self.writeElements(elements)
        # write along steps
        if self.nbSteps > 0:
            for itS in range(self.nbSteps):
                # add fieds
                self.writeContents(fields, numStep=itS)
                # adapt the filename
                filename = self.getFilename(suffix='.' + str(itS).zfill(len(str(self.nbSteps))))
                # write file
                self.write(self.ugrid, filename)
                # update PVD dict
                dataPVD[self.steps[itS]] = filename.name

                # # adapt title
                # self.title = self.adaptTitle(txt=f' step num {itS:d}', append=True)
            # write pvd file
            self.writePVD(dataPVD)
        else:
            # add fieds
            self.writeContents(fields)
            # write file
            filename = self.getFilename()
            self.write(self.ugrid, filename)

    def writePVD(self, dataPVD):
        """Write pvd file"""
        filename = self.getFilename(extension='.pvd')
        # create root element
        root = etree.Element('VTKFile', type='Collection', version='0.1')

        # Create collection elements
        collection = etree.SubElement(root, 'Collection')

        # Loop on timesteps and files for dataset
        for timestep, file in dataPVD.items():
            dataset = etree.Element('DataSet', timestep=str(timestep), part='0', file=file)
            collection.append(dataset)

        # convert xml tree to string
        xml_str = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')

        # write in file
        with open(filename, 'wb') as f:
            f.write(xml_str)

        Logger.debug(f"PVD file '{filename}' successfully written")

    @various.timeit('Fields declared')
    def writeContents(self, fields, numStep=None):
        """
        Add fields depending on version
        """
        self.writeFields(fields, numStep=numStep)

    def writeFields(self, fields, numStep=None):
        """Write fields"""
        if fields is not None:
            if not isinstance(fields, list):
                fields = [fields]
            Logger.info(f'Add {len(fields)} fields')
            for f in fields:
                data, typedata = self.setField(f, numStep=numStep)
                if typedata == 'nodal':
                    self.ugrid.GetPointData().AddArray(data)
                elif typedata == 'elemental':
                    self.ugrid.GetCellData().AddArray(data)

    @various.timeit('Nodes declared')
    def writeNodes(self, nodes):
        """
        Add nodes depending on version
        """
        points = vtk.vtkPoints()
        for i in range(len(nodes)):
            points.InsertNextPoint(nodes[i, :])
        self.ugrid.SetPoints(points)

    @various.timeit('Elements declared')
    def writeElements(self, elements):
        """
        Add elements depending on version
        """
        for m in elements:
            # get connectivity data
            typeElem = m.get('type')
            connectivity = m.get('connectivity')
            physgrp = m.get('physgrp', None)
            # load element's vtk class
            cell, nbnodes = dbvtk.getVTKObj(typeElem)
            Logger.debug(f'Set {len(connectivity)} elements of type {typeElem}')
            #
            for t in connectivity:
                for i in range(nbnodes):
                    cell.GetPointIds().SetId(i, t[i])
                self.ugrid.InsertNextCell(cell.GetCellType(), cell.GetPointIds())

    def createNewFields(self, elems):
        """
        Prepare new fields from elems data (for instance physical group)
        """
        # check if physgroup exists
        physGrp = False
        newFields = None
        for itE in elems:
            if configMESH.DFLT_PHYS_GRP in itE.keys():
                physGrp = True
                break
        if physGrp:
            newFields = list()
            data = list()
            for itE in elems:
                nbElems = itE[configMESH.DFLT_MESH].shape[0]
                if configMESH.DFLT_PHYS_GRP in itE.keys():
                    dataPhys = np.array(itE[configMESH.DFLT_PHYS_GRP], dtype=int)
                    if len(dataPhys) == nbElems:
                        data = np.append(data, dataPhys)
                    else:
                        data = np.append(data, dataPhys[0] * np.ones(nbElems))
                else:
                    data = np.append(data, -np.ones(nbElems))
            Logger.debug('Create new field for physical group')
            newFields.extend([{'data': data, 'type': 'elemental', 'dim': 1, 'name': configMESH.DFLT_PHYS_GRP}])

        return newFields

    def setField(self, field, numStep=None):
        """ """
        # load field data
        data = field.get('data')
        name = field.get('name')
        numEntities = field.get('numEntities', None)
        nbsteps = field.get('nbsteps', 1)
        steps = field.get('steps', None)
        dim = field.get('dim', 0)
        typeField = field.get('type')
        # for time dependent data
        if numStep is not None:
            if nbsteps > 1 or steps is not None:
                data = data[numStep]
        # initialize VTK's array
        dataVtk = ns.numpy_to_vtk(data)
        # dataVtk = vtk.vtkDoubleArray()
        dataVtk.SetName(name)
        # if len(data.shape) == 1:
        #     dim = 1
        # else:
        #     dim = data.shape[1]
        # for _,c in enumerate(data):
        #     if dim == 1:
        #         dataVtk.InsertNextValue(c)
        #     elif dim == 2:
        #         dataVtk.InsertNextTuple2(*c)
        #     elif dim == 3:
        #         dataVtk.InsertNextTuple3(*c)
        #     elif dim == 4:
        #         dataVtk.InsertNextTuple4(*c)
        #     elif dim == 6:
        #         dataVtk.InsertNextTuple6(*c)
        #     elif dim == 9:
        #         dataVtk.InsertNextTuple9(*c)
        # #
        return dataVtk, typeField

    def write(self, ugrid=None, filename=None):
        """
        Write Paraview's files along time steps
        """
        # initialization
        if self.writer is None:
            self.writer = vtk.vtkXMLUnstructuredGridWriter()
            self.writer.SetInputDataObject(self.ugrid)
            if self.binary:
                self.writer.SetFileType(vtk.VTK_BINARY)
            if self.ascii:
                self.writer.SetDataModeToAscii()
        self.writer.SetFileName(filename)
        self.writer.Update()
        # self.writer.SetDebug(True)
        # self.writer.SetWriteTimeValue(True)
        self.writer.Write()
