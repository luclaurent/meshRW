"""
This class is a part of the SILEX library and will write results in legacy VTK file. 
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""

from datetime import datetime
from pathlib import Path

import numpy
from loguru import logger as Logger

from . import configMESH, dbvtk, fileio


class vtkWriter:

    def __init__(self,
                 filename=None,
                 nodes=None,
                 elems=None,
                 fields=None,
                 append=False,
                 title=None,
                 type='v2'):
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
            type (optional, default: 'v2') : XMl format (v2 or XML) 

        """
        #
        self.append = append
        self.type = type.lower()
        self.title = self.adaptTitle(txt=title)
        self.filename = Path(filename)
        #
        self.nbNodes = 0
        self.nbElems = 0
        # check fields for steps
        nbSteps = 0
        iXSteps = list()    # list of fields declared along steps
        # prepare new fields (from physical groups for instance)
        newFields = self.createNewFields(elems)
        if newFields:
            if not fields:
                fields = list()
            fields.extend(newFields)
        # check for data along steps
        if fields is not None:
            for ix, itF in enumerate(fields):
                if configMESH.DFLT_FIELD_STEPS in itF.keys():
                    nbSteps = numpy.max(
                        [nbSteps, len(itF[configMESH.DFLT_FIELD_STEPS])])
                    if len(itF[configMESH.DFLT_FIELD_STEPS]) > 1:
                        iXSteps.append(ix)
                elif configMESH.DFLT_FIELD_NBSTEPS in itF.keys():
                    nbSteps = numpy.max(
                        [nbSteps, itF[configMESH.DFLT_FIELD_NBSTEPS]])
                    if itF[configMESH.DFLT_FIELD_NBSTEPS] > 1:
                        iXSteps.append(ix)

        # write along steps
        if nbSteps > 0:
            for itS in range(nbSteps):
                # adapt title
                self.title = self.adaptTitle(
                    txt=f' step num {itS:d}', append=True)
                # adapt the filename
                filename = self.getFilename(
                    suffix='.' + str(itS).zfill(len(str(nbSteps))))
                self.customHandler = fileio.fileHandler(filename=filename,
                                                        append=self.append,
                                                        safeMode=False)
                # prepare fields (only write all fields on the first step)
                fieldsOk = list()
                fieldsOk = fields
                Logger.info(f'Start writing {self.customHandler.filename}')
                self.writeContents(nodes, elems, fieldsOk, numStep=itS)
                self.customHandler.close()
        else:
            filename = self.getFilename()
            self.customHandler = fileio.fileHandler(filename=filename,
                                                    append=self.append,
                                                    safeMode=False)
            Logger.info(f'Start writing {self.customHandler.filename}')
            self.writeContents(nodes, elems, fields)
            self.customHandler.close()

        Logger.info('Done')

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

    def adaptTitle(self, txt='', append=False):
        """
        """
        if append:
            txtFinal = self.title + txt
        else:
            txtFinal = txt
        if not txtFinal:
            txtFinal = datetime.today().strftime('%Y-%M-%d %H:%M:%s')
        return txtFinal

    def getAppend(self):
        """
        Obtain the adapt flag from the handler (automatic adaptation if the file exists)
        """
        self.append = self.customHandler.append
        return self.append

    def getFilename(self, prefix=None, suffix=None):
        """
        Add prefix and/or suffix to the filename
        """
        path, basename, extension = self.splitFilename()
        if prefix is not None:
            basename = prefix + basename
        if suffix is not None:
            basename = basename + suffix
        return path / (basename + extension)

    def splitFilename(self):
        """
        Get the basename and extension (in list) of the filename
        """
        extension = ''
        filename = self.filename
        it = 0
        while it < 2:
            path = self.filename.parent
            filename = self.filename.stem
            ext = self.filename.suffix
            extension += ext
            if extension in dbvtk.ALLOWED_EXTENSIONS:
                it = 3
            else:
                it += 1
            if it == 2:
                self.logBadExtension()
        return path,filename, extension

    def logBadExtension(self):
        """
        """
        Logger.error('File {}: bad extension (ALLOWED: {})'.format(
            self.filename, ' '.join(dbvtk.ALLOWED_EXTENSIONS)))

    def writeHeader(self):
        """ 
        Write header of the VTK file
        """
        if self.type == 'v2':
            headerVTKv2(self.customHandler.fhandle, commentTxt=self.title)
        elif self.type == 'xml':
            self.headerVTKXML(self.customHandler.fhandle)

    def writeNodes(self, nodes):
        """
        Write elements depending on version
        """
        # count number of nodes
        self.nbNodes = nodes.shape[0]
        if self.type == 'v2':
            WriteNodesV2(self.customHandler.fhandle, nodes)
        elif self.type == 'xml':
            WriteNodesXML(self.customHandler.fhandle, nodes)

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

        if self.type == 'v2':
            WriteElemsV2(self.customHandler.fhandle, elems)
        elif self.type == 'xml':
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
                    dataPhys = numpy.array(
                        itE[configMESH.DFLT_PHYS_GRP], dtype=int)
                    if len(dataPhys) == nbElems:
                        data = numpy.append(data, dataPhys)
                    else:
                        data = numpy.append(
                            data, dataPhys[0]*numpy.ones(nbElems))
                else:
                    data = numpy.append(data, -numpy.ones(nbElems))
            Logger.debug('Create new field for physical group')
            newFields.extend([{'data': data, 'type': 'elemental_scalar',
                             'dim': 1, 'name': configMESH.DFLT_PHYS_GRP}])

        return newFields

    def writeFields(self, fields, numStep=None):
        """
        Write fields depending on version
        """
        if self.type == 'v2':
            WriteFieldsV2(self.customHandler.fhandle,
                          self.nbNodes, self.nbElems, fields, numStep)
        elif self.type == 'xml':
            WriteFieldsXML(self.customHandler.fhandle,
                           self.nbNodes, self.nbElems, fields, numStep)


# classical function to write contents
# write header in VTK file
def headerVTKv2(fileHandle, commentTxt=''):
    fileHandle.write(f'{dbvtk.DFLT_HEADER_VERSION}\n')
    fileHandle.write(f'{commentTxt}\n')
    fileHandle.write(f'{dbvtk.DFLT_TYPE_ASCII}\n')
    fileHandle.write(f'{dbvtk.DFLT_TYPE_MESH}\n')


def headerVTKXML(fileHandle, commentTxt=''):
    pass

# write nodes in VTK file


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

# write elements in VTK file


def WriteElemsV2(fileHandle, elements):
    """Write elements for unstructured grid"""
    # count data
    nbElems = 0
    nbInt = 0
    for itE in elements:
        nbElems += itE[configMESH.DFLT_MESH].shape[0]
        nbInt += numpy.prod(itE[configMESH.DFLT_MESH].shape)
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


def WriteFieldsV2(fileHandle,
                  nbNodes,
                  nbElems,
                  fields,
                  numStep=None):
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
    if len(iXElementalField)+len(iXElementalScalar) > 0:
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
            fileHandle.write('{} {} {:d}\n'.format(
                dbvtk.DFLT_FIELD, 'cellField', len(iXElementalField)))
            for iX in iXElementalField:
                # get array of data
                data = getData(fields[iX], numStep)
                writeFieldsDataV2(fileHandle, data, fields[iX]['name'])

    # write POINT_DATA
    if len(iXNodalField)+len(iXNodalScalar) > 0:
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
            fileHandle.write('{} {} {:d}\n'.format(
                dbvtk.DFLT_FIELD, 'pointField', len(iXNodalField)))
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
    if issubclass(data.dtype.type, numpy.integer):
        dataType = 'int'
        formatSpec = ' '.join('{:d}' for _ in range(nbComp)) + '\n'
    elif issubclass(data.dtype.type, numpy.floating):
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
    if issubclass(data.dtype.type, numpy.integer):
        dataType = 'int'
        formatSpec = ' '.join('{:d}' for _ in range(nbComp)) + '\n'
    elif issubclass(data.dtype.type, numpy.floating):
        dataType = 'double'
        formatSpec = ' '.join('{:9.4f}' for _ in range(nbComp)) + '\n'
    # start writing
    Logger.debug(f'Start writing {dbvtk.DFLT_FIELD} {name}')
    fileHandle.write(f'{name} {nbComp:d} {data.shape[0]:d} {dataType}\n')
    for d in data:
        fileHandle.write(formatSpec.format(*d))


def WriteFieldsXML(fileHandle,
                   nbNodes,
                   nbElems,
                   fields,
                   numStep=None):
    """Write elements"""
