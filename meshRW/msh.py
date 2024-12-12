"""
This class is a part of
the SILEX library and
will write results in msh v2 file.
Documentation available here:
https://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""

import os
import numpy
from . import dbmsh
from . import configMESH
import logging
from . import customLogging, fileio

# load Logger
Logger = logging.getLogger(__name__)
# if not Logger.hasHandlers():
#     LogObj = customLogging.customLogger(loggerRoot=Logger,activate=True)
#     Logger = LogObj.getLogger()


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
    elementDict = dbmsh.loadElementDict()

    # depending on the type of txtEltype
    # - if int: return txtEltype
    # - else get the number from the dictionary
    if isinstance(txtEltype, int):
        elementNum = txtEltype
    else:
        elementNum = elementDict[txtEltype.upper()]
    # show error if the type is not available
    if not elementNum:
        Logger.error('Element type {} not implemented'.format(txtEltype))
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
    elementDict = dbmsh.loadElementDict()
    globalName = None
    # get the name of the element using the integer iD along the dictionary
    for i in elementDict:
        if elementDict[i] == elementNum:
            globalName = i
            break
    # if the name of the element if not available show error
    if globalName is None:
        Logger.error('Element type not found with id {}'.format(elementNum))
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
    nodesPerElem = dbmsh.loadNodesElement()
    nbNodes = 0
    # check if the type of element exists
    if txtElemtype in nodesPerElem.keys():
        # get the number of nodes for the type of element
        nbNodes = nodesPerElem[txtElemtype]
    else:
        # show error message if the type of element does not exist
        Logger.error('Element type {} not defined'.format(txtElemtype))
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


class mshWriter:
    nbNodes = None
    nbElems = None
    dimPb = None
    appendTxt = False
    fhandle = None

    def __init__(self,
                 filename=None,
                 nodes=None,
                 elems=None,
                 fields=None,
                 append=False):
        """
        load class to write file

        syntax:
            mshWriter(filename,nodes,elems,fields)

        inputs:
            filename : string, name of the gmsh file (with or without msh extension),
                                may contain a directory name
            nodes    : nodes coordinates
            elements : connectivity tables (could contains many kind of elements)
                    list of connectivity dict such as [{'connectivity':table1,'type':eltype1,'physgrp':gpr1},{connectivity':table2,'type':eltype1,'physgrp':grp2}...] 
                    'connectivity': connectivity array
                    'type': type of elements (could be a string or an integer, see getGmshElemType and  gmsh documentation)
                    'physgrp' (optional): physical group (integer or array of integers to declare the physical group of each cell)
            fields (optional)  : list of the fields to write, syntax:
                fields=[{'data':variable_name1,'type':'nodal' or 'elemental' ,'dim':number of values per node,'name':'name 1','steps':list of steps,'nbsteps':number of steps],
                        {'data':variable_name2,'type':'nodal' or 'elemental' ,'dim':number of values per node,'name':'name 2','steps':list of steps,'nbsteps':number of steps],
                        ...
                        ]
                append (optional, default: False) : append field to an existing file

        """
        #
        self.basename = os.path.basename(filename)
        # depending on the case
        Logger.info('Start writing {}'.format(self.basename))
        if fields is not None and append and os.path.exists(filename):
            self.fhandle = fileio.fileHandler(
                filename=filename, right='a', safeMode=False)
            self.appendTxt = True
        else:
            self.fhandle = fileio.fileHandler(
                filename=filename, right='w', safeMode=False)

        if not self.appendTxt:
            # write header
            self.fhandle.write('{}\n'.format(
                dbmsh.DFLT_FILE_OPEN_CLOSE['open']))
            self.fhandle.write('{}\n'.format(dbmsh.DFLT_FILE_VERSION))
            self.fhandle.write('{}\n'.format(
                dbmsh.DFLT_FILE_OPEN_CLOSE['close']))
            # write nodes
            self.writeNodes(nodes)
            # write elements
            self.writeElements(elems)

        # write fields
        if fields is not None:
            self.writeFields(elems, fields)

        # close file
        self.fhandle.close()
        self.fhandle = None

        Logger.info('Done')

    def writeNodes(self, nodes):
        """
        write nodes coordinates
        """
        self.nbNodes = nodes.shape[0]
        Logger.debug('Write {} nodes'.format(self.nbNodes))
        #
        self.fhandle.write('{}\n'.format(dbmsh.DFLT_NODES_OPEN_CLOSE['open']))
        self.fhandle.write('{}\n'.format(self.nbNodes))
        #
        self.dimPb = nodes.shape[1]

        # (2d)
        if self.dimPb == 2:
            #
            formatSpec = '{:d} {:9.4g} {:9.4g} 0.0\n'
            # write
            for i in range(self.nbNodes):
                self.fhandle.write(formatSpec.format(i+1, *nodes[i, :], 0.0))

        # (3d)
        if self.dimPb == 3:
            #
            formatSpec = '{:d} {:9.4g} {:9.4g} {:9.4g}\n'
            # write
            for i in range(self.nbNodes):
                self.fhandle.write(formatSpec.format(i+1, *nodes[i, :]))

        self.fhandle.write('{}\n'.format(dbmsh.DFLT_NODES_OPEN_CLOSE['close']))
        Logger.debug('Write nodes: done')

    def writeElements(self, elems):
        """
        write elements
        input:
            elems: lists of dict of connectivity with elements type (could be reduce to only one dictionary and elements)
                    [{'connectivity':table1,'type':eltype1,'physgrp':gpr1},{connectivity':table2,'type':eltype1,'physgrp':grp2}...]
                    or
                    {'connectivity':table1,'type':eltype1,'physgrp':gpr1}

                    'connectivity': connectivity array
                    'type': type of elements (could be a string or an integer, see getGmshElemType and  gmsh documentation)
                    'physgrp' (optional): physical group (integer or array of integers to declare the physical group of each cell)
        """
        # convert to list if dict
        if type(elems) is dict:
            elemsRun = [elems]
        else:
            elemsRun = elems

        # count number of elems
        self.nbElems = 0
        Logger.debug('Start preparing elements')
        for iD in elemsRun:
            dimC = iD[configMESH.DFLT_MESH].shape
            #
            iD['nbElems'] = dimC[0]  # nb of elements on the connectivity table
            iD['nbNodes'] = dimC[1]  # nb of nodes per element
            self.nbElems += dimC[0]  # total number of elements
            #
            # convert element type to MSH number
            iD['eltypeGMSH'] = getMSHElemType(iD[configMESH.DFLT_TYPE_ELEM])
            #
            if not configMESH.DFLT_PHYS_GRP in iD.keys():
                iD[configMESH.DFLT_PHYS_GRP] = 0
            if type(iD[configMESH.DFLT_PHYS_GRP]) is int:
                iD[configMESH.DFLT_PHYS_GRP] = [iD[configMESH.DFLT_PHYS_GRP]]
            if len(iD[configMESH.DFLT_PHYS_GRP]) == 1:
                iD[configMESH.DFLT_PHYS_GRP].append(
                    iD[configMESH.DFLT_PHYS_GRP][0])
        Logger.debug('Done')

        # write all meshes
        Logger.debug('Start writing {} elements'.format(self.nbElems))
        self.fhandle.write('{}\n'.format(dbmsh.DFLT_ELEMS_OPEN_CLOSE['open']))
        self.fhandle.write('{}\n'.format(self.nbElems))
        itElem = 0  # iterator for elements
        for iD in elemsRun:
            # create format specifier for element
            # 1: number of element
            # 2: type of the element (see gmsh documentation)
            # 3: number of tags (minimum number=2)
            # 4: physical entity
            # 5: elementary entity
            # 6+: nodes of the elements
            formatSpec = ' '.join('{:d}' for i in range(
                3+len(iD[configMESH.DFLT_PHYS_GRP])+iD['nbNodes'])) + '\n'
            # write
            for e in range(iD['nbElems']):
                itElem += 1
                # write in file
                self.fhandle.write(formatSpec.format(itElem, iD['eltypeGMSH'], len(
                    iD[configMESH.DFLT_PHYS_GRP]), *iD[configMESH.DFLT_PHYS_GRP], *iD[configMESH.DFLT_MESH][e]))

        self.fhandle.write('{}\n'.format(dbmsh.DFLT_ELEMS_OPEN_CLOSE['close']))
        Logger.debug('Write elements: done')

    def writeFields(self, elems, fields):
        """
        write fields
        input:
            elems: lists of dict of connectivity with elements type (could be reduce to only one dictionary and elements)
                    [{'connectivity':table1,'type':eltype1,'physgrp':gpr1},{connectivity':table2,'type':eltype1,'physgrp':grp2}...]
                    or
                    {'connectivity':table1,'type':eltype1,'physgrp':gpr1}

                    'connectivity': connectivity array
                    'type': type of elements (could be a string or an integer, see getGmshElemType and  gmsh documentation)
                    'physgrp' (optional): physical group (integer or array of integers to declare the physical group of each cell)
            fields=[{'data':variable_name1,'type':'nodal' or 'elemental' ,'dim':number of values per node,'name':'name 1','steps':list of steps,'nbsteps':number of steps],
                        {'data':variable_name2,'type':'nodal' or 'elemental' ,'dim':number of values per node,'name':'name 2','steps':list of steps,'nbsteps':number of steps],
                        ...
                        ]

                    'data': array of the data or list of dictonary
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
        # convert to list if dict
        if fields is dict:
            fieldsRun = [fields]
        else:
            fieldsRun = fields

        # along data
        Logger.debug('Start writing fields')
        for iF in fieldsRun:
            nameField = iF[configMESH.DFLT_FIELD_NAME]
            # number of data per nodes/cells
            nbPerEntity = iF[configMESH.DFLT_FIELD_DIM]
            if configMESH.DFLT_FIELD_STEPS in iF.keys():
                listSteps = iF[configMESH.DFLT_FIELD_STEPS]
                nbSteps = len(listSteps)
            elif configMESH.DFLT_FIELD_NBSTEPS in iF.keys():
                nbSteps = iF[configMESH.DFLT_FIELD_NBSTEPS]
                listSteps = range(nbSteps)
            else:
                nbSteps = 1
                listSteps = [0.0]
            Logger.debug('Field: {}, number of steps: {}, dimension per node/cell: {}'.format(
                nameField, nbSteps, nbPerEntity))
            # reformat values as list of arrays
            if len(iF[configMESH.DFLT_FIELD_DATA]) > 1 and nbSteps == 1:
                values = [iF[configMESH.DFLT_FIELD_DATA]]
            else:
                values = iF[configMESH.DFLT_FIELD_DATA]
            # format specifier to write fields
            formatSpec = '{:d} ' + \
                ' '.join('{:9.4f}' for i in range(nbPerEntity))+'\n'
            # along steps
            for iS in range(nbSteps):
                if nbSteps > 1:
                    Logger.debug('Step number: {}/{}'.format(iS+1, nbSteps))
                if iF[configMESH.DFLT_FIELD_TYPE] == configMESH.DFLT_FIELD_TYPE_NODAL:
                    typeData = dbmsh.DFLT_FIELDS_NODES_OPEN_CLOSE
                elif iF[configMESH.DFLT_FIELD_TYPE] == configMESH.DFLT_FIELD_TYPE_ELEMENT:
                    typeData = dbmsh.DFLT_FIELDS_ELEMS_OPEN_CLOSE
                self.fhandle.write('{}\n'.format(typeData['open']))
                self.fhandle.write('1\n')  # one string tag
                # the name of the view
                self.fhandle.write('"{}"\n'.format(nameField))
                self.fhandle.write('1\n')  # one real tag
                self.fhandle.write('{:9.4f}\n'.format(
                    listSteps[iS]))  # the time value
                self.fhandle.write('3\n')  # three integer tags
                self.fhandle.write('{:d}\n'.format(iS))  # time step value
                # number of components per nodes
                self.fhandle.write('{:d}\n'.format(nbPerEntity))
                # number of nodal values
                self.fhandle.write('{:d}\n'.format(values[iS].shape[0]))
                #
                for i in range(values[iS].shape[0]):
                    self.fhandle.write(
                        formatSpec.format(i+1, *values[iS][i, :]))

                self.fhandle.write('{}\n'.format(typeData['close']))
            Logger.debug('Write field: done')


class mshReader:

    nodes = None  # array of nodes coordinates
    dim = None  # dimension of the mesh (2/3)
    nbNodes = None  # number of nodes
    elems = {}  # dictionary of elements (keys are name of the element)
    tagsList = {}  # list of tags and associated elements
    fhandle = None
    objFile = None
    readData = None
    curIt = 0

    def __init__(self, filename=None, type='mshv2', dim=3):

        Logger.debug('Open file {}'.format(filename))
        # open file and get handle
        self.objFile = fileio.fileHandler(
            filename=filename, right='r', safeMode=False)
        self.fhandle = self.objFile.getHandler()
        # read file line by line
        for l in self.fhandle:
            if not self.readData:
                self.readData = catchTag(l)
            elif self.readData == 'nodes':
                # read nodes
                self.readNodes(dim, l)
            elif self.readData == 'elems':
                # read elements
                self.readElements(l)

        # close file
        self.objFile.close()

    def readNodes(self, dim=None, lineStr=None):
        """
        Read nodes in msh file from line
            imputs: 
                - dim (optional): dimension of the nodes (2D/3D)
                - lineStr: content of the current line
        """
        contentLine = lineStr.split()
        # first read: access to the number of nodes
        if self.curIt == 0:
            # read number of nodes
            self.nbNodes = int(contentLine[0])
            self.curIt += 1
            self.dim = dim
            Logger.debug('Start read {} nodes'.format(self.nbNodes))
        else:
            if self.curIt == 1:
                if not dim:
                    # extract dimension
                    self.dim = len(contentLine)-1
                # create array to store nodes coordinates
                self.nodes = numpy.zeros((self.nbNodes, self.dim))
            # store nodes
            self.nodes[self.curIt-1, :] = numpy.array(
                contentLine[1:self.dim+1], dtype=float)
            self.curIt += 1
            # stop read nodes
            if self.curIt-1 == self.nbNodes:
                self.readData = None
                self.curIt = 0
                Logger.debug('Nodes read: {}, dimension: {}'.format(
                    self.nbNodes, self.dim))

    def readElements(self, lineStr=None):
        """
        Read elements
        imput: 
                - lineStr: content of the current line
        """

        contentLine = lineStr.split()
        # first read: access to the number of elements
        if self.curIt == 0:
            # read number of elements
            self.nbElems = int(contentLine[0])
            self.curIt += 1
            Logger.debug('Start read {} elements'.format(self.nbElems))
        else:
            # store elements connectivity
            self._readElementsLine(contentLine)
            self.curIt += 1
            # stop read nodes
            if self.curIt-1 == self.nbElems:
                #  finalize data
                self._finalizeElems()
                # reset
                self.readData = None
                self.curIt = 0
                Logger.debug('Elements read: {}'.format(self.nbElems))
                Logger.debug('Type of elements')
                for elemType in self.elems.keys():
                    Logger.debug(' > {} {}'.format(
                        self.elems[elemType].shape[0], elemType))
                Logger.debug('Tags')
                for tagName in self.tagsList.keys():
                    Logger.debug('Tag: {}'.format(tagName))
                    for elemType in self.tagsList[tagName].keys():
                        Logger.debug(' > {} {}'.format(
                            len(self.tagsList[tagName][elemType]), elemType))

    def _finalizeElems(self):
        """
        finalize data
        """
        for iT in self.elems:
            self.elems[iT] = numpy.array(self.elems[iT])

    def _readElementsLine(self, arraystr):
        """
        Read a line for elements
        input:
            - arraystr: content of a line for element (array of string)
        """
        # convert to int
        arrayint = numpy.array(arraystr, dtype=int)
        # get element id
        elementId = arrayint[1]
        elemType = getElemTypeFromMSH(elementId)
        # get number of tags
        nbTags = arrayint[2]
        tags = arrayint[3:3+nbTags]
        # element nodes
        elementNodes = arrayint[3+nbTags:]
        # check if element can be stored
        print(self.elems.keys())
        print(elemType)
        
        if elemType not in self.elems.keys():
            self.elems[elemType] = list()
        # store it
        print(type(self.elems[elemType]))
        self.elems[elemType].append(elementNodes)
        # get the item of the element
        iX = len(self.elems[elemType])-1
        # create the list for each tag
        for iT in tags:
            iTs = str(iT)
            # check if the tag already exists
            if iTs not in self.tagsList.keys():
                self.tagsList[iTs] = dict()
            # check if the element type has been already created
            if elemType not in self.tagsList[iTs].keys():
                self.tagsList[iTs][elemType] = list()
            # store the elements
            self.tagsList[iTs][elemType].append(iX)

    def getNodes(self):
        """
        Return the array of nodes coordinates
        """
        return self.nodes

    def getElements(self, type = None, tag = None, dictFormat = True):
        """
        Return elements list
        Inputs:
            - type (optional): choice the type of elements (using gmsh element id or general name of elements)
            - tag (option): choice of the tag (to export a specific part of the mesh)
        """
        elemsTag = dict()
        # filter by tag
        if tag:
            if str(tag) in self.tagsList.keys():
                elemsTag = self.tagsList[str(tag)]
        else:
            # copy all meshes associated to all tags
            # along tags
            for iT, vT in self.tagsList.items():
                # along meshes in tag
                for iM in vT.keys():
                    # check if element type already exists
                    if not iM in elemsTag.keys():
                        elemsTag[iM] = list()
                    elemsTag[iM].extend(vT[iM])
        # filter by type
        if type:
            elemsExport = list()
            elemsExportUnique = list()
            if type in elemsTag.keys():
                elemsExport = self.elems[type][elemsTag[type], :]
                elemsExportUnique = numpy.unique(elemsExport)
        else:
            elemsExport = dict()
            elemsExportUnique = dict()
            for iT in elemsTag.keys():
                elemsExport[iT] = self.elems[iT][elemsTag[iT], :]
                elemsExportUnique[iT] = numpy.unique(elemsExport[iT])

        #specific export
        if not dictFormat and not type:
            if len(elemsExport) > 1:
                Logger.warning('Elements exported without the dictionary format: some data are not exported')
            idElems = list(elemsExport.keys())[0]
            elemsExport = elemsExport[idElems]
            elemsExportUnique = elemsExportUnique[idElems]

        return elemsExport, elemsExportUnique

    def getTags(self):
        """
        Return the list of tags (integer)
        """
        listTags = list()
        listExport = list()
        if self.tagsList:
            listTags = self.tagsList.keys()
            # convert to integer
            for iL in listTags:
                listExport.append(int(iL))
        return listExport

    def getTypes(self):
        """
        Return the list of tags (integer)
        """
        listTypes = list()
        if self.elems:
            listTypes = list(self.elems.keys())
        return listTypes


def catchTag(content=None):
    """
    Try to find a specific tag in content
    """
    tagStartNodes = dbmsh.DFLT_NODES_OPEN_CLOSE['open']
    tagStartElems = dbmsh.DFLT_ELEMS_OPEN_CLOSE['open']
    typeTag = None
    if tagStartNodes == content.strip():
        typeTag = 'nodes'
    if tagStartElems == content.strip():
        typeTag = 'elems'
    return typeTag


def checkContentLine(content=None,
                     pattern=None,
                     item=0):
    """
    check if the pattern could be found exactly in content (list)
    """
    status = True
    if not content:
        status = False
    if not pattern:
        status = False
    if len(content) == 0:
        status = False

    if status:
        if content[0] != pattern:
            status = False
    return status
