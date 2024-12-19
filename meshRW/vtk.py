"""
This class is a part of the SILEX library and will write results in legacy VTK file.
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""

from pathlib import Path
from typing import Union

import numpy as np
from loguru import logger as Logger

from . import configMESH, dbvtk, fileio, various, writerClass


class vtkWriter(writerClass.writer):
    def __init__(
        self,
        filename: Union[str, Path] = None,
        nodes: Union[list, np.ndarray] = None,
        elements: dict = None,
        fields: Union[list, np.ndarray] = None,
        append: bool = False,
        title: str = None,
        opts: dict = {'version': 'v2'},
    ):
        """
        load class to write file

        syntax:
            vtkWriter(filename,nodes,elems,fields)

        inputs:
            filename : string, name of the gmsh file (with or without msh extension),
                                may contain a directory name
            nodes    : nodes coordinates
            elems : connectivity tables (could contains many kind of elements)
                    list of connectivity dict such as [{connectivity:table1,'type':eltype1,phygrp:gpr1},{connectivity':table2,'type':eltype1,configMESH.DFLT_PHYS_GRP:grp2}...]
                    connectivity: connectivity array
                    'type': type of elements (could be a string or an integer, see getGmshElemType and  gmsh documentation)
                    configMESH.DFLT_PHYS_GRP (optional): physical group (integer or array of integers to declare the physical group of each cell)
            fields (optional)  : list of the fields to write, syntax:
                fields=[{'data':variable_name1,'type':'nodal' or 'elemental' ,'dim':number of values per node/cell,'name':'name 1','steps':list of steps,'nbsteps':number of steps],
                        {'data':variable_name2,'type':'nodal' or 'elemental' ,'dim':number of values per node/cell,'name':'name 2','steps':list of steps,'nbsteps':number of steps],
                        ...
                        ]
            append (optional, default: False) : append field to an existing file
            title (optional, default: None) : title of the file
            opts (optional): dictionary of options (version: VTK's format (v2 (default) or XML)

        """
        Logger.info('Start writing vtk file')
        # adapt inputs
        nodes, elements, fields = writerClass.adaptInputs(nodes, elements, fields)
        # prepare new fields (from physical groups for instance)
        newFields = self.createNewFields(elements)
        if newFields:
            if not fields:
                fields = list()
            fields.extend(newFields)
        # initialization
        super().__init__(filename, nodes, elements, fields, append, title, opts)
        # load specific configuration
        self.db = dbvtk
        # write contents depending on the number of steps
        self.writeContentsSteps(nodes, elements, fields)

    def setOptions(self, options: dict):
        """Default options"""
        self.version = options.get('version', 'v2')

    def writeContentsSteps(self, nodes, elements, fields=None):
        """Write content along steps"""
        # write along steps
        if self.nbSteps > 0:
            for itS in range(self.nbSteps):
                # adapt title
                self.title = self.adaptTitle(txt=f' step num {itS:d}', append=True)
                # adapt the filename
                filename = self.getFilename(suffix='.' + str(itS).zfill(len(str(self.nbSteps))))
                self.customHandler = fileio.fileHandler(filename=filename, append=self.append, safeMode=False)
                # prepare fields (only write all fields on the first step)
                fieldsOk = list()
                fieldsOk = fields
                Logger.info(f'Start writing {self.customHandler.filename}')
                self.writeContents(nodes, elements, fieldsOk, numStep=itS)
                self.customHandler.close()
        else:
            filename = self.getFilename()
            self.customHandler = fileio.fileHandler(filename=filename, append=self.append, safeMode=False)
            Logger.info(f'Start writing {self.customHandler.filename}')
            self.writeContents(nodes, elements, fields)
            self.customHandler.close()

    def writeContents(self, nodes, elements, fields=None, numStep=None):
        """
        Write all contents for one step
        """
        # if we are not appending to an existing file
        if not self.getAppend():
            # write header
            self.writeHeader()
            # write nodes
            self.writeNodes(nodes)
            # write elements
            self.writeElements(elements)
        # write fields if available
        if fields is not None:
            self.writeFields(fields, numStep)

    def getAppend(self):
        """
        Obtain the adapt flag from the handler (automatic adaptation if the file exists)
        """
        self.append = self.customHandler.append
        return self.append

    def logBadExtension(self):
        """ """
        Logger.error('File {}: bad extension (ALLOWED: {})'.format(self.filename, ' '.join(dbvtk.ALLOWED_EXTENSIONS)))

    def writeHeader(self):
        """
        Write header of the VTK file
        """
        if self.version == 'v2':
            headerVTKv2(self.customHandler.fhandle, commentTxt=self.title)
        elif self.version == 'xml':
            self.headerVTKXML(self.customHandler.fhandle)

    @various.timeit('Nodes written')
    def writeNodes(self, nodes):
        """
        Write nodes depending on version
        """
        # count number of nodes
        self.nbNodes = nodes.shape[0]
        if self.version == 'v2':
            WriteNodesV2(self.customHandler.fhandle, nodes)
        elif self.version == 'xml':
            WriteNodesXML(self.customHandler.fhandle, nodes)

    @various.timeit('Elements written')
    def writeElements(self, elems):
        """
        Write elements depending on version
        """
        # convert to list if dict
        if type(elems) is dict:
            elemsRun = [elems]
        else:
            elemsRun = elems
        # count number of elements
        self.nbElems = 0
        for e in elemsRun:
            self.nbElems += e[configMESH.DFLT_MESH].shape[0]

        if self.version == 'v2':
            WriteElemsV2(self.customHandler.fhandle, elems)
        elif self.version == 'xml':
            WriteElemsXML(self.customHandler.fhandle, elems)

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
            newFields.extend([{'data': data, 'type': 'elemental_scalar', 'dim': 1, 'name': configMESH.DFLT_PHYS_GRP}])

        return newFields

    @various.timeit('Fields written')
    def writeFields(self, fields, numStep=None):
        """
        Write fields depending on version
        """
        if self.version == 'v2':
            WriteFieldsV2(self.customHandler.fhandle, self.nbNodes, self.nbElems, fields, numStep)
        elif self.version == 'xml':
            WriteFieldsXML(self.customHandler.fhandle, self.nbNodes, self.nbElems, fields, numStep)


# classical function to write contents
# write header in VTK file
def headerVTKv2(fileHandle, commentTxt=''):
    fileHandle.write(f'{dbvtk.DFLT_HEADER_VERSION}\n')
    fileHandle.write(f'{commentTxt}\n')
    fileHandle.write(f'{dbvtk.DFLT_TYPE_ASCII}\n')
    fileHandle.write(f'{dbvtk.DFLT_TYPE_MESH}\n')


def headerVTKXML(fileHandle, commentTxt=''):
    pass


def WriteNodesV2(fileHandle, nodes):
    """Write nodes coordinates for unstructured grid"""
    nbNodes = nodes.shape[0]
    Logger.debug(f'Write {nbNodes} nodes')
    fileHandle.write(f'\n{dbvtk.DFLT_NODES} {nbNodes:d} {dbvtk.DFLT_DOUBLE}\n')
    #
    dimPb = nodes.shape[1]

    # declare format specification
    if dimPb == 2:
        formatSpec = '{:9.4g} {:9.4g}\n'
    elif dimPb == 3:
        formatSpec = '{:9.4g} {:9.4g} {:9.4g}\n'
    # write coordinates
    for i in range(nbNodes):
        fileHandle.write(formatSpec.format(*nodes[i, :]))


def WriteNodesXML(fileHandle, nodes):
    """Write nodes coordinates for unstructured grid"""


def WriteElemsV2(fileHandle, elements):
    """Write elements for unstructured grid"""
    # count data
    nbElems = 0
    nbInt = 0
    for itE in elements:
        nbElems += itE[configMESH.DFLT_MESH].shape[0]
        nbInt += np.prod(itE[configMESH.DFLT_MESH].shape)
        Logger.debug(f'{itE[configMESH.DFLT_MESH].shape[0]} {itE[configMESH.DFLT_FIELD_TYPE]}')

    # initialize size declaration
    fileHandle.write(f'\n{dbvtk.DFLT_ELEMS} {nbElems:d} {nbInt+nbElems:d}\n')
    Logger.debug(f'Start writing {nbElems} {dbvtk.DFLT_ELEMS}')
    # along the element types
    for itE in elements:
        # get the numbering the the element and the number of nodes per element
        nbNodesPerCell = dbvtk.getNumberNodes(itE[configMESH.DFLT_FIELD_TYPE])
        formatSpec = '{:d} '
        formatSpec += ' '.join('{:d}' for _ in range(nbNodesPerCell))
        formatSpec += '\n'
        # write cells
        for e in itE[configMESH.DFLT_MESH]:
            fileHandle.write(formatSpec.format(nbNodesPerCell, *e))

    # declaration of cell types
    fileHandle.write(f'\n{dbvtk.DFLT_ELEMS_TYPE} {nbElems:d}\n')
    Logger.debug(f'Start writing {nbElems} {dbvtk.DFLT_ELEMS_TYPE}')
    # along the element types
    for itE in elements:
        numElemVTK, _ = dbvtk.getVTKElemType(itE[configMESH.DFLT_FIELD_TYPE])
        for _ in range(itE[configMESH.DFLT_MESH].shape[0]):
            fileHandle.write(f'{numElemVTK:d}\n')


def WriteElemsXML(fileHandle, elements):
    """Write elements  for unstructured grid"""


def WriteFieldsV2(fileHandle, nbNodes, nbElems, fields, numStep=None):
    """
        write fields
    input:
        elems: lists of dict of connectivity with elements type (could be reduce to only one dictionary and elements)
                [{'connectivity':table1,'type':eltype1,physgrp:gpr1},{'connectivity':table2,'type':eltype1,configMESH.DFLT_PHYS_GRP:grp2}...]
                or
                {'connectivity':table1,'type':eltype1,'physgrp':gpr1}

                'connectivity': connectivity array
                'type': type of elements (could be a string or an integer, see getGmshElemType and  gmsh documentation)
                'physgrp' (optional): physical group (integer or array of integers to declare the physical group of each cell)
        fields=[{'data':variable_name1,'type':'nodal' or 'elemental' ,'dim':number of values per node,'name':'name 1','steps':list of steps,'nbsteps':number of steps],
                    {'data':variable_name2,'type':'nodal' or 'elemental' ,'dim':number of values per node,'name':'name 2','steps':list of steps,'nbsteps':number of steps],
                    ...
                    ]

                'data': array of the data or list of dictionary
                'type': ('nodal' or 'elemental') data given at nodes or cells
                'dim': number of data per nodes/cells
                'name': name of the data
                'steps' (optional): list of steps used to declare fields
                'nbsteps' (optional): number of steps used to declare fields
                if no 'steps' or 'nbsteps' are declared the field is assumed to be not defined along steps
                #
                'data' could be defined as
                     - list of a arrays with all nodal or elemental values along steps
                     - a dictionary {'array':ar,'connectivityId':int} in the case of elemental
                        'connectivityId': the data are given associated to a certain list of cells (other is defined as 0)

    """
    # analyze fields data
    iXNodalField = list()
    iXElementalField = list()
    iXNodalScalar = list()
    iXElementalScalar = list()
    for i, f in enumerate(fields):
        if f[configMESH.DFLT_FIELD_TYPE] == configMESH.DFLT_FIELD_TYPE_NODAL:
            iXNodalField.append(i)
        elif f[configMESH.DFLT_FIELD_TYPE] == configMESH.DFLT_FIELD_TYPE_ELEMENT:
            iXElementalField.append(i)
        elif f[configMESH.DFLT_FIELD_TYPE] == configMESH.DFLT_FIELD_TYPE_NODAL_SCALAR:
            iXNodalScalar.append(i)
        elif f[configMESH.DFLT_FIELD_TYPE] == configMESH.DFLT_FIELD_TYPE_ELEMENT_SCALAR:
            iXElementalScalar.append(i)

    # write CELL_DATA
    if len(iXElementalField) + len(iXElementalScalar) > 0:
        Logger.debug(f'Start writing {nbElems} {dbvtk.DFLT_ELEMS_DATA}')
        fileHandle.write(f'\n{dbvtk.DFLT_ELEMS_DATA} {nbElems:d}\n')

        # write scalars
        if len(iXElementalScalar) > 0:
            for iX in iXElementalScalar:
                # get array of data
                data = getData(fields[iX], numStep)
                writeScalarsDataV2(fileHandle, data, fields[iX]['name'])
        # write fields
        if len(iXElementalField) > 0:
            Logger.debug(f'Start writing {len(iXElementalField)} {dbvtk.DFLT_FIELD}')
            fileHandle.write('{} {} {:d}\n'.format(dbvtk.DFLT_FIELD, 'cellField', len(iXElementalField)))
            for iX in iXElementalField:
                # get array of data
                data = getData(fields[iX], numStep)
                writeFieldsDataV2(fileHandle, data, fields[iX]['name'])

    # write POINT_DATA
    if len(iXNodalField) + len(iXNodalScalar) > 0:
        Logger.debug(f'Start writing {nbNodes} {dbvtk.DFLT_NODES_DATA}')
        fileHandle.write(f'\n{dbvtk.DFLT_NODES_DATA} {nbNodes:d}\n')
        # write scalars
        if len(iXNodalScalar) > 0:
            for iX in iXNodalScalar:
                # get array of data
                data = getData(fields[iX], numStep)
                writeScalarsDataV2(fileHandle, data, fields[iX]['name'])
        # write fields
        if len(iXNodalField) > 0:
            Logger.debug(f'Start writing {len(iXNodalField)} {dbvtk.DFLT_FIELD}')
            fileHandle.write('{} {} {:d}\n'.format(dbvtk.DFLT_FIELD, 'pointField', len(iXNodalField)))
            for iX in iXNodalField:
                # get array of data
                data = getData(fields[iX], numStep)
                writeFieldsDataV2(fileHandle, data, fields[iX]['name'])


def getData(data, num):
    """
    get data for the right step
    """
    # create array of data
    dataOut = None
    if configMESH.DFLT_FIELD_STEPS in data.keys():
        if len(data[configMESH.DFLT_FIELD_STEPS]) > 1:
            dataOut = data[configMESH.DFLT_FIELD_DATA][num]
    elif configMESH.DFLT_FIELD_NBSTEPS in data.keys():
        if data[configMESH.DFLT_FIELD_NBSTEPS] > 0:
            dataOut = data[configMESH.DFLT_FIELD_DATA][num]
    else:
        dataOut = data[configMESH.DFLT_FIELD_DATA]
    return dataOut


def writeScalarsDataV2(fileHandle, data, name):
    """
    write data using SCALARS
    """
    if len(data.shape) > 1:
        nbComp = data.shape[1]
    else:
        nbComp = 1
    # dataType
    dataType = 'double'
    formatSpec = ' '.join('{:9.4f}' for _ in range(nbComp)) + '\n'
    if issubclass(data.dtype.type, np.integer):
        dataType = 'int'
        formatSpec = ' '.join('{:d}' for _ in range(nbComp)) + '\n'
    elif issubclass(data.dtype.type, np.floating):
        dataType = 'double'
        formatSpec = ' '.join('{:9.4f}' for _ in range(nbComp)) + '\n'
    Logger.debug(f'Start writing {dbvtk.DFLT_SCALARS} {name}')
    fileHandle.write(f'{dbvtk.DFLT_SCALARS} {name} {dataType} {nbComp:d}\n')
    fileHandle.write(f'{dbvtk.DFLT_TABLE} {dbvtk.DFLT_TABLE_DEFAULT}\n')
    for d in data:
        fileHandle.write(formatSpec.format(d))


def writeFieldsDataV2(fileHandle, data, name):
    """
    write data using FIELD
    """
    nbComp = data.shape[1]
    # dataType
    dataType = 'double'
    formatSpec = ' '.join('{:9.4f}' for _ in range(nbComp)) + '\n'
    if issubclass(data.dtype.type, np.integer):
        dataType = 'int'
        formatSpec = ' '.join('{:d}' for _ in range(nbComp)) + '\n'
    elif issubclass(data.dtype.type, np.floating):
        dataType = 'double'
        formatSpec = ' '.join('{:9.4f}' for _ in range(nbComp)) + '\n'
    # start writing
    Logger.debug(f'Start writing {dbvtk.DFLT_FIELD} {name}')
    fileHandle.write(f'{name} {nbComp:d} {data.shape[0]:d} {dataType}\n')
    for d in data:
        fileHandle.write(formatSpec.format(*d))


def WriteFieldsXML(fileHandle, nbNodes, nbElems, fields, numStep=None):
    """Write elements"""
