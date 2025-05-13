"""
This file is part of the meshRW package
---
This class is a part of the SILEX library and will write results in legacy VTK file.
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""

from pathlib import Path
from typing import Union, Optional
import sys

import numpy as np
from loguru import logger as Logger

from . import configMESH, dbvtk, fileio, various, writerClass


class vtkWriter(writerClass.writer):
    """
    vtkWriter is a class designed to write VTK files in various formats (v2 or XML). 
    It supports writing nodes, elements, and fields, and can handle multiple steps 
    for time-dependent data. The class provides flexibility in appending data to 
    existing files and creating new fields based on physical groups.

    Attributes:
        version (str): The VTK format version ('v2' or 'xml').
        nbNodes (int): Number of nodes in the mesh.
        nbElems (int): Number of elements in the mesh.
        append (bool): Flag indicating whether to append to an existing file.
        customHandler (fileio.fileHandler): File handler for writing data.
        db (module): Database module for VTK-specific configurations.

    Methods:
        __init__(filename, nodes, elements, fields, append, title, opts):
            Initializes the vtkWriter instance and prepares the data for writing.
        setOptions(options):
            Sets default options for the writer.
        writeContentsSteps(nodes, elements, fields):
            Writes the content of the VTK file across multiple steps.
        writeContents(nodes, elements, fields, numStep):
            Writes all contents for a single step.
        getAppend():
            Determines whether to append to an existing file.
        logBadExtension():
            Logs an error if the file extension is invalid.
        writeHeader():
            Writes the header of the VTK file based on the version.
        writeNodes(nodes):
            Writes the nodes to the VTK file.
        writeElements(elems):
            Writes the elements to the VTK file.
        createNewFields(elems):
            Creates new fields based on the physical groups in the elements.
        writeFields(fields, numStep):
            Writes the fields to the VTK file based on the version.
    """
    def __init__(        
        self,
        filename: Union[str, Path] = None,
        nodes: Union[list, np.ndarray] = None,
        elements: dict = None,
        fields: Union[list, np.ndarray] = None,
        append: bool = False,
        title: str = None,
        verbose: bool = False,
        opts: dict = {'version': 'v2'},
    ):
        """
        Initialize the VTK writer class.
        Args:
            filename (Union[str, Path], optional): The file path to save the VTK file. Defaults to None.
            nodes (Union[list, np.ndarray], optional): List or array of node coordinates. Defaults to None.
            elements (dict, optional): Dictionary containing element connectivity. Defaults to None.
            fields (Union[list, np.ndarray], optional): List or array of field data. Defaults to None.
            append (bool, optional): Whether to append to an existing file. Defaults to False.
            title (str, optional): Title of the VTK file. Defaults to None.
            verbose (bool, optional): Enable verbose logging if True. Defaults to False.
            opts (dict, optional): Additional options for the writer, such as version. Defaults to {'version': 'v2'}.
        Notes:
            - Adapts verbosity of the logger based on the `verbose` flag.
            - Prepares new fields from physical groups if applicable.
            - Initializes the parent class with the provided parameters.
            - Loads specific configuration for VTK writing.
            - Writes contents depending on the number of steps.
        """
        
        # # adapt verbosity logger
        # if not verbose:
        #     Logger.remove()
        #     Logger.add(sys.stderr, level="INFO") 
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

    def setOptions(self, options: dict)-> None:
        """
        Set the options for the object.

        This method allows setting various configuration options for the object.
        If an option is not provided, a default value will be used.

        Args:
            options (dict): A dictionary containing configuration options. 
                            Supported keys:
                            - 'version' (str): The version to set. Defaults to 'v2'.

        Returns:
            None
        """
        self.version = options.get('version', 'v2')

    def writeContentsSteps(self, 
                           nodes: Union[list, np.ndarray], 
                           elements: dict, 
                           fields: Optional[Union[list, np.ndarray]] = None)-> None:
        """
        Write content along multiple steps or a single step.

        This method handles the writing of mesh data (nodes, elements, and optional fields)
        either across multiple steps or as a single step, depending on the value of `self.nbSteps`.

        Args:
            nodes (Union[list, np.ndarray]): The list or array of nodes to be written.
            elements (dict): A dictionary containing element data to be written.
            fields (Optional[Union[list, np.ndarray]]): Optional list or array of fields to be written.
                If provided, these fields will be written along with the nodes and elements.
                Defaults to None.

        Behavior:
            - If `self.nbSteps > 0`, the method iterates over the number of steps (`self.nbSteps`),
              adapting the title and filename for each step, and writes the contents for each step.
            - If `self.nbSteps == 0`, the method writes the contents as a single step.

        Notes:
            - The filename for each step is generated using `self.getFilename` with a suffix
              corresponding to the step number, zero-padded to match the number of steps.
            - The `self.customHandler` is used to handle file operations, and it is closed
              after writing the contents.
            - Logging is performed to indicate the start of writing for each file.

        Raises:
            Any exceptions raised by the underlying file handling or writing operations
            will propagate up to the caller.
        """
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

    def writeContents(self, 
                      nodes: Union[list, np.ndarray], 
                      elements: dict, 
                      fields: Optional[Union[list, np.ndarray]] = None, 
                      numStep: Optional[int] = None) -> None:
        """
        Writes the contents of a mesh, including nodes, elements, and optional fields, to a file.

        Parameters:
            nodes (Union[list, np.ndarray]): The list or array of nodes to be written.
            elements (dict): A dictionary containing the elements of the mesh.
            fields (Optional[Union[list, np.ndarray]]): Optional list or array of fields to be written. Defaults to None.
            numStep (Optional[int]): Optional step number associated with the fields. Defaults to None.

        Behavior:
            - If appending to an existing file is not enabled, writes the header, nodes, and elements.
            - If fields are provided, writes the fields for the specified step.

        Returns:
            None
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

    def getAppend(self)-> bool:
        """
        Retrieves the 'append' flag from the custom handler.

        This method accesses the 'append' attribute from the customHandler
        to determine whether automatic adaptation should occur if the file exists.

        Returns:
            bool: The value of the 'append' flag indicating whether to append data.
        """
        self.append = self.customHandler.append
        return self.append

    def logBadExtension(self)-> None:
        """
        Logs an error message indicating that the file has a bad extension.

        This method uses the Logger to report that the file associated with 
        this instance has an extension that is not in the list of allowed 
        extensions.

        Args:
            None

        Returns:
            None
        """
        Logger.error('File {}: bad extension (ALLOWED: {})'.format(self.filename, ' '.join(dbvtk.ALLOWED_EXTENSIONS)))

    def writeHeader(self)-> None:
        """
        Write the header of the VTK file based on the specified version.

        This method writes the appropriate header for the VTK file depending on 
        the version specified in the `self.version` attribute. It supports two 
        versions:
        - 'v2': Writes a VTK version 2 header using the `headerVTKv2` function.
        - 'xml': Writes an XML-based VTK header using the `headerVTKXML` method.

        The header is written to the file handle provided by `self.customHandler.fhandle`.

        Raises:
            AttributeError: If `self.version` is not set to a supported value.
        """
        if self.version == 'v2':
            headerVTKv2(self.customHandler.fhandle, commentTxt=self.title)
        elif self.version == 'xml':
            headerVTKXML(self.customHandler.fhandle)

    @various.timeit('Nodes written')
    def writeNodes(self, nodes: np.ndarray) -> None:
        """
        Writes the provided nodes to a file based on the specified version.

        Parameters:
        -----------
        nodes : np.ndarray
            A NumPy array containing the node data to be written. Each row 
            typically represents a node, and columns represent its attributes 
            (e.g., coordinates).

        Notes:
        ------
        - The number of nodes is determined from the shape of the `nodes` array 
          and stored in the `self.nbNodes` attribute.
        - The writing process depends on the `self.version` attribute:
            - If `self.version` is 'v2', the `WriteNodesV2` function is used.
            - If `self.version` is 'xml', the `WriteNodesXML` function is used.
        - The file handle for writing is accessed via `self.customHandler.fhandle`.
        """
        # count number of nodes
        self.nbNodes = nodes.shape[0]
        if self.version == 'v2':
            WriteNodesV2(self.customHandler.fhandle, nodes)
        elif self.version == 'xml':
            WriteNodesXML(self.customHandler.fhandle, nodes)

    @various.timeit('Elements written')
    def writeElements(self, elems: Union[list, np.ndarray, dict]) -> None:
        """
        Writes elements to a file based on the specified version.

        Parameters:
        -----------
        elems : Union[list, np.ndarray, dict]
            The elements to be written. Can be provided as a list, numpy array, 
            or dictionary. If a dictionary is provided, it will be converted 
            into a list for processing.

        Behavior:
        ---------
        - Counts the total number of elements and updates `self.nbElems`.
        - Depending on the version (`self.version`), delegates the writing 
          process to the appropriate function:
            - 'v2': Uses `WriteElemsV2` to write elements.
            - 'xml': Uses `WriteElemsXML` to write elements.

        Raises:
        -------
        None
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

    def createNewFields(self, elems: Union[list, np.ndarray, dict]) -> Optional[list]:
        """
        Create new fields based on the provided elements data.

        This method processes the input `elems` to prepare new fields, particularly
        for physical groups if they exist in the data. It checks for the presence
        of a physical group key (`configMESH.DFLT_PHYS_GRP`) in the elements and
        creates a new field accordingly.

        Args:
            elems (Union[list, np.ndarray, dict]): A collection of elements data.
                Each element is expected to be a dictionary containing mesh data
                and optionally a physical group identifier.

        Returns:
            Optional[list]: A list of dictionaries representing the new fields if
            physical group data is found. Each dictionary contains:
                - 'data': A NumPy array of physical group data for the elements.
                - 'type': The type of the field, e.g., 'elemental_scalar'.
                - 'dim': The dimensionality of the field (e.g., 1).
                - 'name': The name of the field, typically `configMESH.DFLT_PHYS_GRP`.
            Returns `None` if no physical group data is found.
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
    def writeFields(self, fields: Optional[Union[list, np.ndarray]] = None, numStep: Optional[int] = None)-> None:
        """
        Writes field data to a file based on the specified version.

        Parameters:
            fields (Optional[Union[list, np.ndarray]]): The field data to be written. 
                It can be a list or a NumPy array. Defaults to None.
            numStep (Optional[int]): The time step or iteration number associated 
                with the field data. Defaults to None.

        Returns:
            None
        """
        if self.version == 'v2':
            WriteFieldsV2(self.customHandler.fhandle, self.nbNodes, self.nbElems, fields, numStep)
        elif self.version == 'xml':
            WriteFieldsXML(self.customHandler.fhandle, self.nbNodes, self.nbElems, fields, numStep)


# classical function to write contents
# write header in VTK file
def headerVTKv2(fileHandle: fileio.fileHandler, commentTxt: str ='')-> None:
    """
    Writes the header for a VTK file to the provided file handle.

    Parameters:
        fileHandle (fileio.fileHandler): The file handler object used to write to the file.
        commentTxt (str, optional): A comment string to include in the header. Defaults to an empty string.

    Returns:
        None
    """
    fileHandle.write(f'{dbvtk.DFLT_HEADER_VERSION}\n')
    fileHandle.write(f'{commentTxt}\n')
    fileHandle.write(f'{dbvtk.DFLT_TYPE_ASCII}\n')
    fileHandle.write(f'{dbvtk.DFLT_TYPE_MESH}\n')


def headerVTKXML(fileHandle, commentTxt=''):
    pass


def WriteNodesV2(fileHandle: fileio.fileHandler, 
                 nodes: np.ndarray) -> None:
    """
    Write the coordinates of nodes for an unstructured grid to a file.

    Args:
        fileHandle (fileio.fileHandler): A file handler object used to write data to a file.
        nodes (np.ndarray): A 2D NumPy array containing the coordinates of the nodes. 
                            Each row represents a node, and the columns represent the 
                            spatial dimensions (e.g., x, y, z).

    Raises:
        ValueError: If the number of spatial dimensions in the `nodes` array is not 2 or 3.

    Notes:
        - The function writes the number of nodes and their coordinates to the file in a 
          specific format.
        - The format of the coordinates depends on the spatial dimensions of the problem:
          - 2D: Writes x and y coordinates.
          - 3D: Writes x, y, and z coordinates.
    """
    nbNodes = nodes.shape[0]
    Logger.debug(f'Write {nbNodes} nodes')
    fileHandle.write(f'\n{dbvtk.DFLT_NODES} {nbNodes:d} {dbvtk.DFLT_DOUBLE}\n')
    #
    dimPb = nodes.shape[1]

    # declare format specification
    formatSpec = None
    if dimPb == 2:
        formatSpec = '{:9.4g} {:9.4g}\n'
    elif dimPb == 3:
        formatSpec = '{:9.4g} {:9.4g} {:9.4g}\n'
    # write coordinates
    for i in range(nbNodes):
        fileHandle.write(formatSpec.format(*nodes[i, :]))


def WriteNodesXML(fileHandle, nodes):
    """Write nodes coordinates for unstructured grid"""
    pass


def WriteElemsV2(fileHandle: fileio.fileHandler, elements: list) -> None:
    """
    Write elements for an unstructured grid to a file.

    This function writes the connectivity and type information of elements
    in an unstructured grid format to the provided file handle.

    Args:
        fileHandle (fileio.fileHandler): A file handler object used to write data to a file.
        elements (list): A list of element data, where each element is a dictionary-like
                         structure containing mesh and field type information.

    The function performs the following steps:
        1. Counts the total number of elements and the total number of integers required
           to represent the connectivity of the elements.
        2. Writes the size declaration for the elements and their connectivity.
        3. Iterates over the element types to write the connectivity of each element
           to the file.
        4. Writes the declaration of cell types for the elements.
        5. Iterates over the element types again to write the VTK element type for each
           element to the file.

    Notes:
        - The function assumes that `configMESH.DFLT_MESH` and `configMESH.DFLT_FIELD_TYPE`
          are keys used to access mesh and field type information in the `elements` list.
        - The `dbvtk.getNumberNodes` function is used to determine the number of nodes
          per element based on the field type.
        - The `dbvtk.getVTKElemType` function is used to determine the VTK element type
          for each field type.

    Raises:
        Any exceptions raised by the file handler or the utility functions used
        within this function.

    Returns:
        None
    """
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
    pass


def WriteFieldsV2(fileHandle: fileio.fileHandler, nbNodes: int, nbElems: int, fields: list, numStep: int = None)-> None:
    """
    Writes nodal and elemental field data to a file in a specific format.

    Parameters:
        fileHandle (fileio.fileHandler): The file handler used to write the data.
        nbNodes (int): The number of nodes in the mesh.
        nbElems (int): The number of elements in the mesh.
        fields (list): A list of dictionaries containing field data. Each dictionary should have the following keys:
            - 'data': Array of the data or a list of dictionaries. For elemental data, it can be a dictionary with keys:
                - 'array': The data array.
                - 'connectivityId': The ID of the connectivity associated with the data.
            - 'type': Specifies whether the data is 'nodal' or 'elemental'.
            - 'dim': The number of data values per node or element.
            - 'name': The name of the data field.
            - 'steps' (optional): A list of steps used to declare fields.
            - 'nbsteps' (optional): The number of steps used to declare fields.
        numStep (int, optional): The specific time step for which data is being written. Defaults to None.

    Field Types:
        - Nodal fields: Data associated with nodes.
        - Elemental fields: Data associated with elements.
        - Nodal scalars: Scalar data associated with nodes.
        - Elemental scalars: Scalar data associated with elements.

    Behavior:
        - Analyzes the fields to classify them into nodal fields, elemental fields, nodal scalars, and elemental scalars.
        - Writes CELL_DATA for elemental fields and scalars.
        - Writes POINT_DATA for nodal fields and scalars.
        - For each field or scalar, retrieves the data for the specified time step (if applicable) and writes it to the file.

    Notes:
        - The function uses helper functions `getData`, `writeScalarsDataV2`, and `writeFieldsDataV2` to process and write the data.
        - The format of the written data is determined by constants such as `dbvtk.DFLT_ELEMS_DATA`, `dbvtk.DFLT_NODES_DATA`, and `dbvtk.DFLT_FIELD`.

    Raises:
        - None explicitly, but errors may occur if the input data is malformed or if file operations fail.
    ##
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


def getData(data: dict, num: int) -> np.ndarray:
    """
    Retrieve data for a specific step from the provided dictionary.

    This function extracts data corresponding to a specific step number
    from a dictionary that contains simulation or field data. The structure
    of the dictionary is expected to include specific keys defined in the
    `configMESH` module.

    Args:
        data (dict): A dictionary containing the data. It is expected to have
                     keys such as `DFLT_FIELD_STEPS`, `DFLT_FIELD_NBSTEPS`, 
                     and `DFLT_FIELD_DATA` as defined in `configMESH`.
        num (int): The step number for which the data is to be retrieved.

    Returns:
        np.ndarray: The data corresponding to the specified step. If no step-specific
                    data is available, it returns the default data.

    Notes:
        - If the key `DFLT_FIELD_STEPS` exists and contains more than one step,
          the function retrieves the data for the specified step.
        - If the key `DFLT_FIELD_NBSTEPS` exists and indicates more than zero steps,
          the function retrieves the data for the specified step.
        - If neither of the above conditions is met, the function returns the default
          data from the `DFLT_FIELD_DATA` key.
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


def writeScalarsDataV2(fileHandle: fileio.fileHandler, data: np.ndarray, name: str) -> None:
    """
    Writes scalar data to a file using the SCALARS format.

    This function writes scalar or vector data to a file in a specific format
    compatible with VTK (Visualization Toolkit). The data can be either integers
    or floating-point numbers, and the function determines the appropriate data
    type and formatting based on the input.

    Args:
        fileHandle (fileio.fileHandler): A file handler object used to write the data.
        data (np.ndarray): A NumPy array containing the scalar or vector data to be written.
                           If the array is 2D, each row is treated as a vector.
        name (str): The name of the scalar data to be written.

    Raises:
        ValueError: If the data type of the input array is not supported.

    Notes:
        - The function writes the data type (`int` or `double`) and the number of components
          (1 for scalars, >1 for vectors) to the file.
        - The data is formatted with a precision of 4 decimal places for floating-point numbers.
        - The function uses a logger to record the start of the writing process.
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


def writeFieldsDataV2(fileHandle: fileio.fileHandler, 
                      data: np.ndarray, 
                      name: str) -> None:
    """
    Writes a 2D NumPy array to a file using a custom FIELD format.

    Parameters:
    -----------
    fileHandle : fileio.fileHandler
        A file handler object used to write data to the file.
    data : np.ndarray
        A 2D NumPy array containing the data to be written. Each row represents
        a data point, and each column represents a component of the data.
    name : str
        The name of the field to be written.

    Notes:
    ------
    - The function determines the data type of the array (integer or floating-point)
      and writes the data accordingly.
    - The FIELD format includes the field name, the number of components per data
      point, the number of data points, and the data type.
    - Each row of the array is written in a formatted style, with floating-point
      numbers formatted to 4 decimal places.

    Example:
    --------
    If `data` is a 2D array with shape (3, 2) and contains floating-point numbers:
        [[1.2345, 2.3456],
         [3.4567, 4.5678],
         [5.6789, 6.7890]]
    The output will include the field name, number of components (2), number of
    data points (3), and the formatted data.
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
    pass
