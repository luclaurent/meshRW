"""
This file is part of the meshRW package
---
This class will write results in msh v2 file.
Documentation available here:
https://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""

from pathlib import Path
from typing import IO, Optional, Union, cast, Iterable

import numpy as np
from loguru import logger as Logger

from . import configMESH, dbmsh, fileio, various, writerClass



class MSHWriter(writerClass.Writer):
    """
    Write legacy Gmsh v2 mesh files.

    The writer emits geometry/connectivity and optional nodal or elemental result
    fields using the text MSH v2 layout. When ``append`` is enabled and the target
    file already exists, only field sections are appended.

    Attributes:
        db (module): Database module for GMSH configurations.
        fhandle (fileio.fileHandler): File handler for writing data to the file.
        nbNodes (int): Number of nodes in the mesh.
        dimPb (int): Dimensionality of the problem (2D or 3D).
        nbElems (int): Number of elements in the mesh.
    Methods:
        The writer provides dedicated routines for nodes, elements, and fields,
        and supports appending additional field blocks to existing MSH files.
    Usage:
        Use this class to create or append legacy `.msh` outputs from array-like
        mesh and field data structures.
    Example:
        writer = MSHWriter(
            filename="mesh.msh",
            nodes=[[0, 0, 0], [1, 0, 0], [0, 1, 0]],
            elements=[{'connectivity': [[1, 2, 3]], 'type': 'triangle'}],
            fields=[{'data': [[1.0, 2.0, 3.0]], 'type': 'nodal', 'dim': 1, 'name': 'Temperature'}],
            append=False,
            title="Example Mesh",
            verbose=True
    """

    def __init__(
        self,
        filename: Union[str, Path, None] = None,
        nodes: Union[list, np.ndarray, None] = None,
        elements: Union[list, np.ndarray, None] = None,
        fields: Union[list, np.ndarray, None] = None,
        append: bool = False,
        title: str|None = None,
        verbose: bool = False,
        opts: dict|None = None,
    )-> None:
        """
        Initialize the legacy Gmsh writer.

        Parameters:
            filename (Union[str, Path], optional): Name of the GMSH file (with or without `.msh` extension).
                Can include a directory path. Defaults to None.
            nodes (Union[list, np.ndarray], optional): Node coordinates. Defaults to None.
            elements (Union[list, np.ndarray], optional): Connectivity tables. Should be a dictionary 
                or list of dictionaries
                with keys:
                    - 'connectivity': Connectivity array.
                    - 'type': Type of elements (string or integer, see GMSH documentation).
                    - 'physgrp' (optional): Physical group (integer or array of integers for each cell).
                Defaults to None.
            fields (Union[list, np.ndarray], optional): List of fields to write. Each field is a dictionary with keys:
                - 'data': Array-like values, or a list of arrays for time-dependent exports.
                - 'type': 'nodal' or 'elemental'.
                - 'dim': Number of values per node.
                - 'name': Name of the field.
                - 'steps': List of steps.
                - 'nbsteps': Number of steps.
                Defaults to None.
            append (bool, optional): Whether to append fields to an existing file. 
            Defaults to False.
            title (str, optional): Title of the file. 
            Defaults to None.
            verbose (bool, optional): If True, enables verbose logging. 
            Defaults to False.
            opts (dict, optional): Additional options for the writer. 
            Defaults: {'createPath': True},.

        Raises:
            Exception: If any error occurs during file handling or writing.

        Notes:
            - This class adapts the inputs for writing and initializes the file handler.
            - Depending on the `append` flag and file existence, the file is opened in append or write mode.
            - The contents are written immediately and the file is closed before returning.
        """
        # # adapt verbosity logger
        # if not verbose:
        #     Logger.remove()
        #     Logger.add(sys.stderr, level="INFO")
        Logger.info('Start writing msh file')
        _ = verbose
        # adapt inputs
        nodesOk, elementsOk, fieldsOk = writerClass.adaptInputs(nodes, elements, fields)
        # initialization
        super().__init__(filename, nodesOk, elementsOk, fieldsOk, append, title, opts)

        # load specific configuration
        self.db = dbmsh
        self.dimPb = 0
        self.nbNodes = 0
        self.nbElems = 0
        # depending on the case
        Logger.info(f'Initialize writing {self.basename}')
        if fields is not None and self.append and self.filename.exists():
            self.fhandle = fileio.fileHandler(filename=filename, right='a', safeMode=False)
        else:
            self.fhandle = fileio.fileHandler(filename=filename, right='w', safeMode=False)

        # write contents
        self.writeContents(nodesOk, elementsOk, fieldsOk)

        # close file
        self.fhandle.close()
        self.fhandle = None

    def setOptions(self, opts: dict)-> None:
        """
        Store writer options.

        Args:
            opts (dict): A dictionary containing configuration options
                    to be set. The keys and values in the dictionary
                    should correspond to the specific options supported
                    by the object.

        Returns:
            None
        """
        self.opts = opts

    def writeContents(self,
                      nodes: Union[list, np.ndarray, None],
                      elements: Union[list, np.ndarray, None],
                      fields: Optional[list|None] = None,
                      numStep: Optional[int|None] = None)-> None:
        """
        Write the contents of a mesh file, including nodes, elements, and optional fields.

        Parameters:
            nodes (Union[list, np.ndarray]): The list or array of nodes to be written to the file.
            elements (Union[list, np.ndarray]): The list or array of elements to be written to the file.
            fields (Optional[list], optional): A list of fields to be written to the file. Defaults to None.
            numStep (Optional[int], optional): Unused placeholder kept for API compatibility with the 
                abstract base class.

        Returns:
            None
        """
        _ = numStep
        if self.fhandle is None:
            Logger.error('File handle is not initialized. Cannot write contents.')
            return
        handle = self.fhandle
        if not self.getAppend():
            # write header
            txt = dbmsh.DFLT_FILE_OPEN_CLOSE['open']
            handle.write(f'{txt}\n')
            handle.write(f'{dbmsh.DFLT_FILE_VERSION}\n')
            txt = dbmsh.DFLT_FILE_OPEN_CLOSE['close']
            handle.write(f'{txt}\n')
            # write nodes
            self.writeNodes(nodes)
            # write elements
            self.writeElements(elements)

        # write fields
        if fields is not None:
            self.writeFields(fields)

    def getAppend(self)-> bool:
        """
        Retrieves the append flag from the file handler.

        This method checks the file handler's `append` attribute to determine
        whether the file is set to append mode. The append mode indicates if
        new data will be added to the existing file content.

        Returns:
            bool: The current state of the append flag.
        """
        if self.fhandle is None:
            return False
        self.append = bool(getattr(self.fhandle, 'append', False))
        return self.append

    @various.timeit('Nodes written')
    def writeNodes(self, nodes: Union[list, np.ndarray, None])-> None:
        """
        Writes the coordinates of nodes to a file in a specific format.

        Parameters:
        -----------
        nodes : Union[list, np.ndarray]
            A list or numpy array containing the coordinates of the nodes. Each node
            is represented as a row, with columns corresponding to its coordinates.
            For 2D problems, each row should have 2 values (x, y). For 3D problems,
            each row should have 3 values (x, y, z).

        Notes:
        ------
        - The method determines the dimensionality of the problem (2D or 3D) based
          on the number of columns in the `nodes` array.
        - For 2D problems, a placeholder value of `0.0` is added as the z-coordinate.
        - The method writes the nodes in a specific format, including an opening
          and closing tag defined in `dbmsh.DFLT_NODES_OPEN_CLOSE`.
        - Node indices in the output file start from 1.
        """
        if self.fhandle is None:
            Logger.error('File handle is not initialized. Cannot write nodes.')
            return
        if nodes is None:
            Logger.warning('No nodes to write')
            return
        handle = self.fhandle
        if handle is None:
            return
        # adapt nodes
        if isinstance(nodes, list):
            nodes = np.array(nodes)
        #
        self.nbNodes = nodes.shape[0]
        Logger.debug(f'Write {self.nbNodes} nodes')
        #
        txt = dbmsh.DFLT_NODES_OPEN_CLOSE['open']
        handle.write(f'{txt}\n')
        handle.write(f'{self.nbNodes}\n')
        #
        self.dimPb = nodes.shape[1]

        # (2d)
        if self.dimPb == 2:
            #
            formatSpec = '{:d} {:9.4g} {:9.4g} 0.0\n'
            # write
            for i in range(self.nbNodes):
                handle.write(formatSpec.format(i + 1, *nodes[i, :], 0.0))

        # (3d)
        if self.dimPb == 3:
            #
            formatSpec = '{:d} {:9.4g} {:9.4g} {:9.4g}\n'
            # write
            for i in range(self.nbNodes):
                handle.write(formatSpec.format(i + 1, *nodes[i, :]))
        txt = dbmsh.DFLT_NODES_OPEN_CLOSE['close']
        handle.write(f'{txt}\n')

    @various.timeit('Elements written')
    def writeElements(self, elements: Union[list, np.ndarray, None])-> None:
        """
        Writes elements to a file in the GMSH format.

        Parameters:
            elements (Union[list, np.ndarray, None]): A list or dictionary containing element connectivity and metadata.
                The input can be one of the following formats:
                    - List of dictionaries:
                        [{'connectivity': table1, 'type': eltype1, 'physgrp': grp1},
                         {'connectivity': table2, 'type': eltype2, 'physgrp': grp2}, ...]
                    - Single dictionary:
                        {'connectivity': table1, 'type': eltype1, 'physgrp': grp1}

                Keys in the dictionary:
                    - 'connectivity': A 2D array representing the connectivity table of elements.
                    - 'type': The type of elements (string or integer, see GMSH documentation).
                    - 'physgrp' (optional): Physical group identifier(s). Can be an integer or 
                    an array of integersto declare the physical group of each cell.
                    Defaults to 0 if not provided.

        Returns:
            None

        Notes:
            - The method calculates the total number of elements (`nbElems`) and 
            writes them to the file.
            - Each element is written with its type, physical group, and connectivity information.
            - The GMSH element type is determined using `dbmsh.getMSHElemType`.
            - Physical group identifiers are adjusted to ensure they are in the correct format 
            (list of integers).
        """
        if self.fhandle is None:
            Logger.error('File handle is not initialized. Cannot write elements.')
            return
        if elements is None:
            Logger.warning('No elements to write')
            return
        handle = self.fhandle
        if handle is None:
            return
        # convert to list if dict
        if isinstance(elements, dict):
            elemsRun = [elements]
        elif isinstance(elements, np.ndarray):
            elemsRun = list(elements)
        else:
            elemsRun = list(elements)

        # count number of elems
        self.nbElems = 0
        Logger.debug('Start preparing elements')
        for iD in elemsRun:
            mesh = iD.get(configMESH.DFLT_MESH)
            if mesh is None:
                raise ValueError('Element connectivity is required')
            mesh_array = np.asarray(mesh, dtype=int)
            iD.update({configMESH.DFLT_MESH: mesh_array})
            dimC = mesh_array.shape
            #
            iD.update({'nbElems': dimC[0]})  # nb of elements on the connectivity table
            iD.update({'nbNodes': dimC[1]})  # nb of nodes per element
            self.nbElems += dimC[0]  # total number of elements
            #
            # convert element type to MSH number
            elemType = iD.get(configMESH.DFLT_TYPE_ELEM)
            if elemType is None:
                raise ValueError('Element type is required')
            iD.update({'eltypeGMSH': dbmsh.getMSHElemType(elemType)})
            #
            phys_grp = iD.get(configMESH.DFLT_PHYS_GRP, 0)
            if isinstance(phys_grp, int):
                phys_grp_list = [phys_grp]
            else:
                phys_grp_list = list(phys_grp)
            if len(phys_grp_list) == 1:
                phys_grp_list.append(phys_grp_list[0])
            iD.update({configMESH.DFLT_PHYS_GRP: phys_grp_list})
        Logger.debug('Done')

        # write all meshes
        Logger.debug(f'Start writing {self.nbElems} elements')
        txt = dbmsh.DFLT_ELEMS_OPEN_CLOSE['open']
        handle.write(f'{txt}\n')
        handle.write(f'{self.nbElems}\n')
        itElem = 0  # iterator for elements
        for iD in elemsRun:
            phys_grp_list = cast(list[int], iD.get(configMESH.DFLT_PHYS_GRP))
            nbNodes = int(iD.get('nbNodes', 0))
            nbElems = int(iD.get('nbElems', 0))
            mesh_array = cast(np.ndarray, iD.get(configMESH.DFLT_MESH))
            msh_type = int(iD.get('eltypeGMSH', 0))
            # create format specifier for element
            # 1: number of element
            # 2: type of the element (see gmsh documentation)
            # 3: number of tags (minimum number=2)
            # 4: physical entity
            # 5: elementary entity
            # 6+: nodes of the elements
            formatSpec = ' '.join('{:d}' for i in range(3 + \
                len(phys_grp_list) + nbNodes)) + '\n'
            # write
            for e in range(nbElems):
                itElem += 1
                # write in file
                handle.write(
                    formatSpec.format(
                        itElem,
                        msh_type,
                        len(phys_grp_list),
                        *phys_grp_list,
                        *mesh_array[e],
                    )
                )
        txt = dbmsh.DFLT_ELEMS_OPEN_CLOSE['close']
        handle.write(f'{txt}\n')

    @various.timeit('Fields written')
    def writeFields(self,
                    fields: Optional[Union[list, np.ndarray, dict]] = None,
                    numStep: Optional[int] = None)-> None:
        """
        Writes field data to a file in a specific format.

        Parameters:
        ----------
        fields : Optional[Union[list, np.ndarray, dict]]
            A list, NumPy array, or dictionary containing field data. The structure of the input is as follows:
            - If a dictionary, it is converted to a list.
            - Each field in the list is a dictionary with the following keys:
                - 'data': Array of the data or a list of dictionaries.
                          If a dictionary, it should have:
                            - 'array': Array of data values.
                            - 'connectivityId': Integer indicating the associated list of cells.
                - 'type': String, either 'nodal' or 'elemental', indicating whether the data is 
                    defined at nodes or cells.
                - 'dim': Integer, the number of data values per node or cell.
                - 'name': String, the name of the data field.
                - 'steps' (optional): List of steps used to declare fields.
                - 'nbsteps' (optional): Integer, the number of steps used to declare fields.
                  If neither 'steps' nor 'nbsteps' are provided, the field is assumed to be static 
                  (not defined along steps).

        Behavior:
        ---------
        - Converts the input fields to a list if it is a dictionary.
        - Iterates through each field and writes its data to the file.
        - Handles both nodal and elemental data types.
        - Supports writing data for multiple time steps if 'steps' or 'nbsteps' are provided.
        - Formats the output using a specific format specifier for each field.

        Notes:
        ------
        - The method uses a predefined configuration (`configMESH`) to extract default 
            field keys and types.
        - Logging is used to provide debug information about the writing process, 
            including field names, steps, and dimensions.
        - The output format includes tags, time values, and data values for each node or cell.

        Raises:
        -------
        - KeyError: If required keys are missing in the input field dictionaries.
        - ValueError: If the field type is neither nodal nor elemental.
        """
        _ = numStep
        assert self.fhandle is not None
        if fields is None:
            return
        # convert to list if dict
        _ = numStep
        if self.fhandle is None:
            Logger.error('File handle is not initialized. Cannot write fields.')
            return
        handle = self.fhandle
        if fields is None:
            return
        if isinstance(fields, dict):
            fieldRun = [fields]
        elif isinstance(fields, np.ndarray):
            fieldRun = list(fields)
        else:
            fieldRun = fields

        # along data
        Logger.debug('Start writing fields')
        for field in fieldRun:
            iF = cast(dict, field)
            nameField = iF[configMESH.DFLT_FIELD_NAME]
            # number of data per nodes/cells
            nbPerEntity = iF[configMESH.DFLT_FIELD_DIM]
            if configMESH.DFLT_FIELD_STEPS in iF:
                listSteps = iF[configMESH.DFLT_FIELD_STEPS]
                nbSteps = len(listSteps)
            elif configMESH.DFLT_FIELD_NBSTEPS in iF:
                nbSteps = iF[configMESH.DFLT_FIELD_NBSTEPS]
                listSteps = range(nbSteps)
            else:
                nbSteps = 1
                listSteps = [0.0]
            txt = f'Field: {nameField}, number of steps: {nbSteps}'
            txt += f', dimension per node/cell: {nbPerEntity}'
            Logger.debug(txt)
            # reformat values as list of arrays
            if len(iF[configMESH.DFLT_FIELD_DATA]) > 1 and nbSteps == 1:
                values = [iF[configMESH.DFLT_FIELD_DATA]]
            else:
                values = iF[configMESH.DFLT_FIELD_DATA]
            # format specifier to write fields
            formatSpec = '{:d} ' + ' '.join('{:9.4f}' for i in range(nbPerEntity)) + '\n'
            # along steps
            for iS in range(nbSteps):
                if nbSteps > 1:
                    Logger.debug(f'Step number: {iS+1}/{nbSteps}')
                if iF[configMESH.DFLT_FIELD_TYPE] == configMESH.DFLT_FIELD_TYPE_NODAL:
                    typeData = dbmsh.DFLT_FIELDS_NODES_OPEN_CLOSE
                elif iF[configMESH.DFLT_FIELD_TYPE] == configMESH.DFLT_FIELD_TYPE_ELEMENT:
                    typeData = dbmsh.DFLT_FIELDS_ELEMS_OPEN_CLOSE
                else:
                    raise ValueError(f"Unknown field type {iF[configMESH.DFLT_FIELD_TYPE]}")
                txt = typeData['open']
                handle.write(f'{txt}\n')
                handle.write('1\n')  # one string tag
                # the name of the view
                handle.write(f'"{nameField}"\n')
                handle.write('1\n')  # one real tag
                handle.write(f'{listSteps[iS]:9.4f}\n')  # the time value
                handle.write('3\n')  # three integer tags
                handle.write(f'{iS:d}\n')  # time step value
                # number of components per nodes
                handle.write(f'{nbPerEntity:d}\n')
                # number of nodal values
                handle.write(f'{values[iS].shape[0]:d}\n')
                #
                for i in range(values[iS].shape[0]):
                    handle.write(formatSpec.format(i + 1, *values[iS][i, :]))

                txt = typeData['close']
                handle.write(f'{txt}\n')


class MSHReader:
    """
    mshReader is a class designed to read and process mesh files in the `.msh` format.
    It provides functionality to parse nodes, elements, and tags from the file and
    organize them into structured data for further use.

    Attributes:
        nodes (numpy.ndarray): Array of node coordinates.
        dim (int): Dimension of the mesh (2D or 3D).
        nbNodes (int): Number of nodes in the mesh.
        elems (dict): Dictionary of elements, where keys are element types and values
        are lists of element connectivity.
        tagsList (dict): Dictionary of tags and associated elements.
        fhandle (file object): File handle for the opened `.msh` file.
        obj_file (fileio.fileHandler): File handler object for managing file operations.
        read_data (str): Current section being read ('nodes', 'elems', or None).
        curIt (int): Current iteration index for reading nodes or elements.

    Methods:
        __init__(filename=None, type='mshv2', dim=3):
            Initializes the MSHReader object, opens the file, and reads its content.

        initContent():
            Initializes or resets the content attributes of the object.

        __del__():
            Destructor method to clean up the object.

        clean():
            Cleans the object by resetting its content attributes.

        readNodes(dim=None, lineStr=None):
            Reads node data from the `.msh` file.
            Args:
                dim (int, optional): Dimension of the nodes (2D or 3D).
                lineStr (str): Content of the current line being read.

        readElements(lineStr=None):
            Reads element data from the `.msh` file.
            Args:
                lineStr (str): Content of the current line being read.

        _finalizeElems():
            Finalizes the element data by converting lists to numpy arrays.

        _readElementsLine(arraystr):
            Reads a single line of element data and processes it.
            Args:
                arraystr (list of str): Content of a line for an element.

        getNodes(tag=None):
            Returns the array of node coordinates.
            Args:
                tag (int, optional): Tag to filter nodes by.

        getElements(type=None, tag=None, dict_format=True):
            Returns the list of elements.
            Args:
                type (str, optional): Type of elements to filter by.
                tag (int, optional): Tag to filter elements by.
                dict_format (bool, optional): Whether to return elements in dictionary format.

        getTags():
            Returns the list of tags as integers.

        getTypes():
            Returns the list of element types.
    """

    def __init__(self,
                 filename: Union[str, Path, None]=None,
                 typeMSH: str='mshv2',
                 dim: int=3)->None:
        """
        Initializes the mesh reader object.

        Args:
            filename (Union[str, Path], optional): The path to the mesh file to be read. 
            Defaults to None.
            type (str, optional): The type of the mesh file. Defaults to 'mshv2'.
            dim (int, optional): The dimensionality of the mesh (e.g., 2D or 3D). 
            Defaults to 3.

        Attributes:
            obj_file (fileio.fileHandler): The file handler object for the mesh file.
            fhandle (file object): The file handle for reading the mesh file.
            read_data (str): Tracks the current section of the file being read 
            (e.g., 'nodes', 'elems').

        Raises:
            Exception: If there are issues with file handling or data parsing.

        Notes:
            - The method reads the mesh file line by line, identifying and processing 
            nodes and elements.
            - After reading, it finalizes the elements and closes the file.
        """
        _ = typeMSH
        self.initContent()
        Logger.debug(f'Open file {filename}')
        # open file and get handle
        self.objFile = fileio.fileHandler(filename=filename, right='r', safeMode=False)
        self.fhandle = cast(IO[str], self.objFile.getHandler())
        # read file line by line
        for line in cast(Iterable[str], self.fhandle):
            if not self.read_data:
                self.read_data = catchTag(line)
            elif self.read_data == 'nodes':
                # read nodes
                self.readNodes(dim, line)
            elif self.read_data == 'elems':
                # read elements
                self.readElements(line)
        # finalize data
        self._finalizeElems()

        # close file
        self.objFile.close()

    def initContent(self)-> None:
        """
        Initializes the content attributes of the mesh object.

        This method sets up the following attributes:
        - `nodes`: An array to store the coordinates of the nodes (initially None).
        - `dim`: The dimension of the mesh (2D or 3D) (initially None).
        - `nbNodes`: The number of nodes in the mesh (initially None).
        - `elems`: A dictionary to store elements, where keys are the names of the elements.
        - `tagsList`: A dictionary to store tags and their associated elements.
        - `fhandle`: A file handle for file operations (initially None).
        - `obj_file`: An object representing the file (initially None).
        - `read_data`: Data read from the file (initially None).
        - `curIt`: An integer representing the current iteration (initially 0).
        """
        self.nodes = None  # array of nodes coordinates
        self.dim = None  # dimension of the mesh (2/3)
        self.nbNodes = None  # number of nodes
        self.elems = {}  # dictionary of elements (keys are name of the element)
        self.tagsList = {}  # list of tags and associated elements
        self.fhandle = None
        self.objFile = None
        self.read_data = None
        self.curIt = 0

    def __del__(self)-> None:
        """
        Destructor method that is automatically called when the object is about to be destroyed.
        Ensures that any necessary cleanup operations are performed by invoking the `clean` method.
        """
        self.clean()

    def clean(self)-> None:
        """
        Cleans the object by reinitializing its content.

        This method resets the object's state by calling the `initContent`
        method, ensuring that any previous data or modifications are cleared.
        """
        self.initContent()

    def readNodes(self, dim: Optional[int]=None, lineStr: Optional[str]=None)-> None:
        """
        Reads node data from a line in an `.msh` file.

        This method processes the node information from a given line of the file,
        storing the number of nodes, their dimensions, and their coordinates.

        Args:
            dim (Optional[int]): The dimension of the nodes (e.g., 2 for 2D, 3 for 3D).
                                 If not provided, it will be inferred from the data.
            lineStr (Optional[str]): The content of the current line being read.

        Behavior:
            - On the first call (`curIt == 0`), it reads the number of nodes (`nbNodes`)
              and initializes the dimension (`dim`).
            - On subsequent calls, it processes the node coordinates and stores them
              in a NumPy array (`nodes`).
            - Once all nodes are read, it resets the reading state (`read_data` and `curIt`).

        Attributes:
            nbNodes (int): The total number of nodes to be read.
            dim (int): The dimension of the nodes (e.g., 2D or 3D).
            nodes (np.ndarray): A NumPy array storing the coordinates of the nodes.
            curIt (int): The current iteration or line being processed.
            read_data (None): A flag indicating the end of the node reading process.

        Logs:
            - Logs the start of the node reading process with the number of nodes.
            - Logs the completion of the node reading process with the total nodes
              and their dimension.
        """
        if lineStr is None:
            return
        contentLine = lineStr.split()
        # first read: access to the number of nodes
        if self.curIt == 0:
            # read number of nodes
            self.nbNodes = int(contentLine[0])
            self.curIt += 1
            self.dim = dim
            Logger.debug(f'Start read {self.nbNodes} nodes')
        else:
            if self.curIt == 1:
                if not dim:
                    # extract dimension
                    self.dim = len(contentLine) - 1
                if self.nbNodes is None or self.dim is None:
                    return
                # create array to store nodes coordinates
                self.nodes = np.zeros((self.nbNodes, self.dim))
            if self.nodes is None or self.dim is None:
                return
            # store nodes
            assert self.nodes is not None and self.dim is not None
            self.nodes[self.curIt - 1, :] = np.array(contentLine[1 : self.dim + 1], dtype=float)
            self.curIt += 1
            # stop read nodes
            if self.curIt - 1 == self.nbNodes:
                self.read_data = None
                self.curIt = 0
                Logger.debug(f'Nodes read: {self.nbNodes}, dimension: {self.dim}')

    def readElements(self, lineStr: Optional[str]=None)-> None:
        """
        Reads and processes elements from a given line of input.

        This method is responsible for parsing and storing element connectivity
        information from a line of input. It handles the initialization of the
        number of elements to read, processes each line of element data, and
        finalizes the data once all elements have been read.

        Args:
            lineStr (Optional[str]): The content of the current line to be processed.
                                     If None, no processing is performed.

        Behavior:
            - On the first call (self.curIt == 0), it reads the total number of elements
              from the input line and initializes the reading process.
            - On subsequent calls, it processes the element connectivity data line by line.
            - Once all elements have been read, it finalizes the data, resets internal
              state variables, and logs the results.

        Logging:
            - Logs the start of the element reading process.
            - Logs the number and type of elements read.
            - Logs the tags associated with the elements.

        Note:
            This method relies on helper methods `_readElementsLine` and `_finalizeElems`
            to process individual lines and finalize the data, respectively.
        """
        if lineStr is None:
            return
        contentLine = lineStr.split()
        # first read: access to the number of elements
        if self.curIt == 0:
            # read number of elements
            self.nbElems = int(contentLine[0])
            self.curIt += 1
            Logger.debug(f'Start read {self.nbElems} elements')
        else:
            # store elements connectivity
            self._readElementsLine(contentLine)
            self.curIt += 1
            # stop read elements
            if self.curIt - 1 == self.nbElems:
                #  finalize data
                self._finalizeElems()
                # reset
                self.read_data = None
                self.curIt = 0
                Logger.debug(f'Elements read: {self.nbElems}')
                Logger.debug('Type of elements')
                for key,val in self.elems.items():
                    Logger.debug(f' > {val.shape[0]} {key}')
                Logger.debug('Tags')
                for k,v in self.tagsList.items():
                    Logger.debug(f'Tag: {k}')
                    for key,val in v.items():
                        Logger.debug(f' > {len(val)} {key}')

    def _finalizeElems(self)-> None:
        """
        Finalizes the element data by converting each element in the `elems` dictionary
        to a NumPy array. This ensures that the data structure is consistent and
        optimized for numerical operations.

        Returns:
            None
        """
        for it in self.elems:
            self.elems[it] = np.array(self.elems[it])

    def _readElementsLine(self, arraystr: list)-> None:
        """
        Reads and processes a line of element data from a mesh file.

        Args:
            arraystr (list): A list of strings representing the content of a line
                             for an element in the mesh file.

        Functionality:
            - Converts the input line to an integer array.
            - Extracts the element ID and determines its type using the 
            `dbmsh.get_elemType_from_msh` function.
            - Retrieves the number of tags and the associated tags from the line.
            - Extracts the nodes associated with the element.
            - Stores the element nodes in the `self.elems` dictionary, categorized by element type.
            - Updates the `self.tagsList` dictionary to associate tags with their corresponding elements
              and element types.

        Notes:
            - The `self.elems` dictionary organizes elements by their type, with each type containing
              a list of node arrays.
            - The `self.tagsList` dictionary maps tags (as strings) to a nested structure of element
              types and their corresponding indices in `self.elems`.

        Raises:
            ValueError: If the input line does not conform to the expected format or contains 
            invalid data.
        """
        # convert to int
        arrayint = np.array(arraystr, dtype=int)
        # get element id
        elementID = arrayint[1]
        elemType = dbmsh.getElemTypeFromMSH(elementID)
        # get number of tags
        nbTags = arrayint[2]
        tags = arrayint[3 : 3 + nbTags]
        # element nodes
        elementNodes = arrayint[3 + nbTags :]
        # check if element can be stored
        if elemType not in self.elems:
            self.elems[elemType] = list()
        # store it
        self.elems[elemType].append(elementNodes)
        # get the item of the element
        ix = len(self.elems[elemType]) - 1
        # create the list for each tag
        for it in tags:
            itS = str(it)
            # check if the tag already exists
            if itS not in self.tagsList:
                self.tagsList[itS] = dict()
            # check if the element type has been already created
            if elemType not in self.tagsList[itS]:
                self.tagsList[itS][elemType] = list()
            # store the elements
            self.tagsList[itS][elemType].append(ix)

    def getNodes(self, tag: Optional[int]=None)-> np.ndarray:
        """
        Retrieve the array of node coordinates.

        Parameters:
        -----------
        tag : int, optional
            If provided, filters the nodes associated with the specified tag.
            The tag corresponds to a specific group of elements.

        Returns:
        --------
        np.ndarray
            A NumPy array containing the coordinates of the nodes. If a tag is
            specified, only the coordinates of the nodes associated with the
            elements of that tag are returned. Otherwise, all node coordinates
            are returned.
        """
        if self.nodes is None:
            return np.array([])
        if tag is not None:
            # get elements
            elts = self.getElements(tag=tag, dictFormat=False)
            if isinstance(elts, dict):
                return np.array([])
            return self.nodes[np.unique(elts.flatten())-1,:]
        return np.array([]) if self.nodes is None else self.nodes

    def getElements(self,
                    typeElem: str|None=None,
                    tag: int|None=None,
                    dictFormat: bool=True)-> Union[np.ndarray, dict]:
        """
        Retrieve elements from the mesh based on specified criteria.

        Parameters:
            typeElem (str, optional): The type of elements to retrieve. This can be specified
                using the Gmsh element ID or the general name of the elements. If not provided,
                elements of all types will be considered.
            tag (int, optional): The tag to filter elements by. If specified, only elements
                associated with the given tag will be retrieved. If not provided, elements
                from all tags will be included.
            dictFormat (bool, optional): Determines the format of the returned data.
                If True, the elements will be returned as a dictionary. If False, the elements
                will be returned as a NumPy array. Defaults to True.

        Returns:
            Union[np.ndarray, dict]: The retrieved elements. The format depends on the
            `dictFormat` parameter:
                - If `dictFormat` is True, a dictionary is returned where keys are element
                  types and values are NumPy arrays of elements.
                - If `dictFormat` is False, a NumPy array of elements is returned. If multiple
                  element types are present, only the first type is returned with a warning.

        Notes:
            - If `type` is specified, only elements of the given type are retrieved.
            - If `tag` is specified, only elements associated with the given tag are retrieved.
            - If `dictFormat` is False and multiple element types are present, only the first
              type is exported, and a warning is logged.
        """
        elemsTag = dict()
        # filter by tag
        if tag:
            if str(tag) in self.tagsList:
                elemsTag = self.tagsList[str(tag)]
        else:
            # copy all meshes associated to all tags
            # along tags
            for _, vT in self.tagsList.items():
                # along meshes in tag
                for iM in vT.keys():
                    # check if element type already exists
                    if iM not in elemsTag:
                        elemsTag[iM] = list()
                    elemsTag[iM].extend(vT[iM])
        # filter by type
        if typeElem:
            elemsExportUnique = np.array([])
            if typeElem in elemsTag.keys():
                elemsExport = self.elems[typeElem][elemsTag[typeElem], :]
                elemsExportUnique = np.unique(elemsExport, axis=0)
        else:
            elemsExport = dict()
            elemsExportUnique = dict()
            for key,val in elemsTag.items():
                elemsExport[key] = self.elems[key][val, :]
                elemsExportUnique[key] = np.unique(elemsExport[key], axis=0)

        # specific export
        if not dictFormat and not typeElem:
            if len(elemsExport) > 1:
                Logger.warning('Elements exported without the dictionary format: some data are not exported')
            if len(elemsExport) == 0:
                Logger.warning('No element to export')
                return np.array([])
            idElems = list(elemsExport)[0]
            elemsExport = elemsExport[idElems]
            elemsExportUnique = elemsExportUnique[idElems]

        return cast(Union[np.ndarray, dict], elemsExportUnique)

    def getTags(self)-> list:
        """
        Retrieves the list of tags as integers.

        This method processes the `tagsList` attribute of the object, which is expected
        to be a dictionary-like structure. It extracts the keys, converts them to integers,
        and returns them as a list.

        Returns:
            list: A list of integer tags. If `tagsList` is empty or not set, an empty 
            list is returned.
        """
        listTags = list()
        listExport = list()
        if self.tagsList:
            listTags = self.tagsList.keys()
            # convert to integer
            for il in listTags:
                listExport.append(int(il))
        return listExport

    def getTypes(self)-> list:
        """
        Retrieve the list of element types (tags) present in the mesh.

        Returns:
            list: A list of integer tags representing the types of elements
                  in the mesh. If no elements are present, an empty list is returned.
        """
        listTypes = list()
        if self.elems:
            listTypes = list(self.elems.keys())
        return listTypes


def catchTag(content: Optional[str] = None)-> Optional[str]:
    """
    Determines the type of tag present in the given content.

    This function checks if the provided content matches specific predefined
    tags for "nodes" or "elems" and returns the corresponding tag type.

    Args:
        content (str, optional): The content to check for a tag. Defaults to None.

    Returns:
        Optional[str]: The type of tag found in the content. Returns 'nodes' if the content
             matches the opening tag for nodes, 'elems' if it matches the opening
             tag for elements, or None if no match is found.
    """
    tagStartNodes = dbmsh.DFLT_NODES_OPEN_CLOSE['open']
    tagStartElems = dbmsh.DFLT_ELEMS_OPEN_CLOSE['open']
    if content is None:
        return None
    typeTag = None
    if tagStartNodes == content.strip():
        typeTag = 'nodes'
    if tagStartElems == content.strip():
        typeTag = 'elems'
    return typeTag


def checkContentLine(content: list|None=None,
                     pattern: str|None=None,
                     item: int=0)-> bool:
    """
    Check if the first element of a list matches a given pattern.

    This function verifies whether the first element of the provided list `content`
    matches the exact value of the string `pattern`. If the list is empty,
    `content` or `pattern` is not provided, or the first element does not match
    the pattern, the function returns `False`.

    Args:
        content (list, optional): The list to check. Defaults to None.
        pattern (str, optional): The string pattern to match. Defaults to None.
        item (int, optional): Unused parameter. Defaults to 0.

    Returns:
        bool: `True` if the first element of `content` matches `pattern`,
              otherwise `False`.
    """
    _ = item
    if not content or not pattern:
        return False
    return content[0] == pattern

writer = MSHWriter
reader = MSHReader
mshWriter = MSHWriter
mshReader = MSHReader
