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
from typing import Iterable, Optional, Union, cast

import numpy as np
from loguru import logger as Logger

from . import config_mesh, dbmsh, fileio, various, writerclass


class MSHWriter(writerclass.Writer):
    """
    MSHWriter is a class for writing GMSH (.msh) files. It provides functionality 
    to write nodes, elements, and fields into a GMSH file format. The class supports
    appending data to existing files and handles various configurations for writing
    mesh data.
    Attributes:
        db (module): Database module for GMSH configurations.
        fhandle (fileio.fileHandler): File handler for writing data to the file.
        nbNodes (int): Number of nodes in the mesh.
        dimPb (int): Dimensionality of the problem (2D or 3D).
        nbElems (int): Number of elements in the mesh.
    Methods:
        __init__(filename, nodes, elements, fields, append, title, verbose, opts):
            Initializes the mshWriter class and writes the contents to the file.
        set_options(options):
            Sets default options for the writer.
        write_contents(nodes, elements, fields, num_step):
            Writes the contents of the mesh file, including nodes, elements, and fields.
        get_append():
            Checks if the file is in append mode.
        write_nodes(nodes):
            Writes the nodes' coordinates to the file.
        write_elements(elems):
            Writes the elements' connectivity and types to the file.
        write_fields(fields):
            Writes the fields (nodal or elemental data) to the file.
    Usage:
        This class is used to create or append to GMSH (.msh) files. It supports writing 
        nodes, elements, and fields with various configurations. The input data can be 
        provided as lists or numpy arrays, and the class handles the formatting and 
        writing process.
    Example:
        writer = mshWriter(
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
        opts: Optional[dict] = None,
    )-> None:
        """
       Initialize the mshWriter class to write a GMSH file.

        Parameters:
            filename (Union[str, Path], optional): Name of the GMSH file (with or without 
            `.msh` extension). 
                Can include a directory path. Defaults to None.
            nodes (Union[list, np.ndarray], optional): Node coordinates. Defaults to None.
            elements (Union[list, np.ndarray], optional): Connectivity tables. Should be a 
            list of dictionaries 
                with keys:
                    - 'connectivity': Connectivity array.
                    - 'type': Type of elements (string or integer, see GMSH documentation).
                    - 'physgrp' (optional): Physical group (integer or array of integers for 
                    each cell). 
                Defaults to None.
            fields (Union[list, np.ndarray], optional): List of fields to write. Each field 
            is a dictionary with keys:
                - 'data': Variable name.
                - 'type': 'nodal' or 'elemental'.
                - 'numentities': Number of concerned values (nodes or elements).
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
            - Depending on the `append` flag and file existence, the file is opened 
            in append or write mode.
            - The contents are written to the file, and the file is closed after writing.
        """
        # # adapt verbosity logger
        # if not verbose:
        #     Logger.remove()
        #     Logger.add(sys.stderr, level="INFO")
        _ = verbose
        Logger.info('Start writing msh file')
        # adapt inputs
        if elements is None:
            raise ValueError('elements are required')
        nodes, elements, fields = writerclass.adapt_inputs(nodes, elements, fields)
        if nodes is None or elements is None:
            raise ValueError('nodes and elements are required')
        # initialization
        super().__init__(filename,
                         nodes,
                         cast(dict | None, elements),
                         fields,
                         append,
                         title,
                         opts or {'createPath': True})

        # load specific configuration
        self.db = dbmsh
        self.opts = opts or {'createPath': True}
        self.nb_nodes = 0
        self.dim_pb = 0
        self.nb_elems = 0
        # depending on the case
        Logger.info(f'Initialize writing {self.basename}')
        if fields is not None and self.append and self.filename.exists():
            self.fhandle = fileio.FileHandler(filename=filename, right='a', safe_mode=False)
        else:
            self.fhandle = fileio.FileHandler(filename=filename, right='w', safe_mode=False)

        # write contents
        self.write_contents(nodes, elements, fields)

        # close file
        self.fhandle.close()
        self.fhandle = None

    def set_options(self, opts: dict)-> None:
        """
        Sets the default options for the object.

        Args:
            opts (dict): A dictionary containing configuration options 
                    to be set. The keys and values in the dictionary 
                    should correspond to the specific options supported 
                    by the object.

        Returns:
            None
        """
        self.opts = opts

    def write_contents(self,
                      nodes: Union[list, np.ndarray],
                      elements: Union[list, np.ndarray],
                      fields: Union[list, np.ndarray, None] = None,
                      num_step: Optional[int] = None)-> None:
        """
        Write the contents of a mesh file, including nodes, elements, and optional fields.

        Parameters:
            nodes (Union[list, np.ndarray]): The list or array of nodes to be written to 
            the file.
            elements (Union[list, np.ndarray]): The list or array of elements to be written
             to the file.
            fields (Optional[list], optional): A list of fields to be written to the file.
             Defaults to None.
            num_step (Optional[int], optional): The step number associated with the fields. 
            Defaults to None.

        Returns:
            None
        """
        _ = num_step
        assert self.fhandle is not None
        if not self.get_append():
            # write header
            txt = dbmsh.DFLT_FILE_OPEN_CLOSE['open']
            self.fhandle.write(f'{txt}\n')
            self.fhandle.write(f'{dbmsh.DFLT_FILE_VERSION}\n')
            txt = dbmsh.DFLT_FILE_OPEN_CLOSE['close']
            self.fhandle.write(f'{txt}\n')
            # write nodes
            self.write_nodes(nodes)
            # write elements
            self.write_elements(elements)

        # write fields
        if fields is not None:
            self.write_fields(fields)

    def get_append(self)-> bool:
        """
        Retrieves the append flag from the file handler.

        This method checks the file handler's `append` attribute to determine
        whether the file is set to append mode. The append mode indicates if
        new data will be added to the existing file content.

        Returns:
            bool: The current state of the append flag.
        """
        assert self.fhandle is not None
        self.append = bool(self.fhandle.append)
        return self.append

    @various.timeit('Nodes written')
    def write_nodes(self, nodes: Union[list, np.ndarray])-> None:
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
        assert self.fhandle is not None
        # adapt nodes
        if isinstance(nodes, list):
            nodes = np.array(nodes)
        #
        self.nb_nodes = nodes.shape[0]
        Logger.debug(f'Write {self.nb_nodes} nodes')
        #
        txt = dbmsh.DFLT_NODES_OPEN_CLOSE['open']
        self.fhandle.write(f'{txt}\n')
        self.fhandle.write(f'{self.nb_nodes}\n')
        #
        self.dim_pb = nodes.shape[1]

        # (2d)
        if self.dim_pb == 2:
            #
            format_spec = '{:d} {:9.4g} {:9.4g} 0.0\n'
            # write
            for i in range(self.nb_nodes):
                self.fhandle.write(format_spec.format(i + 1, *nodes[i, :], 0.0))

        # (3d)
        if self.dim_pb == 3:
            #
            format_spec = '{:d} {:9.4g} {:9.4g} {:9.4g}\n'
            # write
            for i in range(self.nb_nodes):
                self.fhandle.write(format_spec.format(i + 1, *nodes[i, :]))
        txt = dbmsh.DFLT_NODES_OPEN_CLOSE['close']
        self.fhandle.write(f'{txt}\n')

    @various.timeit('Elements written')
    def write_elements(self, elements: Union[list, np.ndarray])-> None:
        """
        Writes elements to a file in the GMSH format.

        Parameters:
            elems (Union[list, np.ndarray]): A list or dictionary containing 
            element connectivity and metadata.
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
        assert self.fhandle is not None
        # convert to list if dict
        if isinstance(elements, dict):
            elems_run = [elements]
        else:
            elems_run = elements

        # count number of elems
        self.nb_elems = 0
        Logger.debug('Start preparing elements')
        dflt_mesh = config_mesh.DFLT_MESH
        dflt_phys_grp = config_mesh.DFLT_PHYS_GRP
        dflt_type_elem = config_mesh.DFLT_TYPE_ELEM
        for elem in elems_run:
            id_elem = cast(dict, elem)
            mesh_data = id_elem.get(dflt_mesh)
            if mesh_data is None:
                raise ValueError(f'Missing {dflt_mesh} in element')
            dim_c = mesh_data.shape
            #
            id_elem['nbElems'] = dim_c[0]  # nb of elements on the connectivity table
            id_elem['nbNodes'] = dim_c[1]  # nb of nodes per element
            self.nb_elems += dim_c[0]  # total number of elements
            #
            # convert element type to MSH number
            elem_type = id_elem.get(dflt_type_elem)
            if elem_type is None:
                raise ValueError(f'Missing {dflt_type_elem} in element')
            id_elem['eltypeGMSH'] = dbmsh.get_msh_elem_type(elem_type)
            #
            if dflt_phys_grp not in id_elem:
                id_elem[dflt_phys_grp] = 0
            phys_grp = id_elem.get(dflt_phys_grp)
            if isinstance(phys_grp, int):
                id_elem[dflt_phys_grp] = [phys_grp]
            phys_grp_list = id_elem.get(dflt_phys_grp)
            if phys_grp_list is not None and len(phys_grp_list) == 1:
                phys_grp_list.append(phys_grp_list[0])
        Logger.debug('Done')

        # write all meshes
        Logger.debug(f'Start writing {self.nb_elems} elements')
        txt = dbmsh.DFLT_ELEMS_OPEN_CLOSE['open']
        self.fhandle.write(f'{txt}\n')
        self.fhandle.write(f'{self.nb_elems}\n')
        it_elem = 0  # iterator for elements
        for elem in elems_run:
            id_elem = cast(dict, elem)
            # create format specifier for element
            # 1: number of element
            # 2: type of the element (see gmsh documentation)
            # 3: number of tags (minimum number=2)
            # 4: physical entity
            # 5: elementary entity
            # 6+: nodes of the elements
            phys_grp = cast(list, id_elem.get(config_mesh.DFLT_PHYS_GRP))
            mesh = cast(np.ndarray, id_elem.get(config_mesh.DFLT_MESH))
            nb_nodes = cast(int, id_elem.get('nbNodes'))
            nb_elems = cast(int, id_elem.get('nbElems'))
            elem_type = cast(int, id_elem.get('eltypeGMSH'))
            format_spec = ' '.join('{:d}' \
                for _ in \
                    range(3 + len(phys_grp) + nb_nodes))\
                    + '\n'
            # write
            for e in range(nb_elems):
                it_elem += 1
                # write in file
                self.fhandle.write(
                    format_spec.format(
                        it_elem,
                        elem_type,
                        len(phys_grp),
                        *phys_grp,
                        *mesh[e],
                    )
                )
        txt = dbmsh.DFLT_ELEMS_OPEN_CLOSE['close']
        self.fhandle.write(f'{txt}\n')

    @various.timeit('Fields written')
    def write_fields(self,
                     fields: Union[list, np.ndarray, None] = None,
                     num_step: Optional[int] = None)-> None:
        """
        Writes field data to a file in a specific format.

        Parameters:
        ----------
        fields : Union[list, np.ndarray]
            A list or dictionary containing field data. The structure of the input is as follows:
            - If a dictionary, it is converted to a list.
            - Each field in the list is a dictionary with the following keys:
                - 'data': Array of the data or a list of dictionaries. 
                          If a dictionary, it should have:
                            - 'array': Array of data values.
                            - 'connectivityId': Integer indicating the associated list of cells.
                - 'type': String, either 'nodal' or 'elemental', indicating whether the data 
                is defined at nodes or cells.
                - 'dim': Integer, the number of data values per node or cell.
                - 'name': String, the name of the data field.
                - 'steps' (optional): List of steps used to declare fields.
                - 'nbsteps' (optional): Integer, the number of steps used to declare fields.
                  If neither 'steps' nor 'nbsteps' are provided, the field is assumed to be 
                  static (not defined along steps).

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
        - Logging is used to provide debug information about the writing process, including 
        field names, steps, and dimensions.
        - The output format includes tags, time values, and data values for each node or 
        cell.

        Raises:
        -------
        - KeyError: If required keys are missing in the input field dictionaries.
        - AttributeError: If the file handle (`self.fhandle`) is not properly initialized.
        """
        _ = num_step
        assert self.fhandle is not None
        if fields is None:
            return
        # convert to list if dict
        if isinstance(fields, dict):
            fields_run = [fields]
        else:
            fields_run = fields

        # along data
        Logger.debug('Start writing fields')
        for field in fields_run:
            it_f = cast(dict, field)
            name_field = it_f[config_mesh.DFLT_FIELD_NAME]
            # number of data per nodes/cells
            nb_per_entity = it_f[config_mesh.DFLT_FIELD_DIM]
            if config_mesh.DFLT_FIELD_STEPS in it_f:
                list_steps = it_f[config_mesh.DFLT_FIELD_STEPS]
                nb_steps = len(list_steps)
            elif config_mesh.DFLT_FIELD_NBSTEPS in it_f:
                nb_steps = it_f[config_mesh.DFLT_FIELD_NBSTEPS]
                list_steps = range(nb_steps)
            else:
                nb_steps = 1
                list_steps = [0.0]
            txt = f'Field: {name_field}, number of steps: {nb_steps}'
            txt += f', dimension per node/cell: {nb_per_entity}'
            Logger.debug(txt)
            # reformat values as list of arrays
            if len(it_f[config_mesh.DFLT_FIELD_DATA]) > 1 and nb_steps == 1:
                values = [it_f[config_mesh.DFLT_FIELD_DATA]]
            else:
                values = it_f[config_mesh.DFLT_FIELD_DATA]
            # format specifier to write fields
            format_spec = '{:d} ' + ' '.join('{:9.4f}' for i in range(nb_per_entity)) + '\n'
            # along steps
            for it_step in range(nb_steps):
                if nb_steps > 1:
                    Logger.debug(f'Step number: {it_step+1}/{nb_steps}')
                if it_f[config_mesh.DFLT_FIELD_TYPE] == config_mesh.DFLT_FIELD_TYPE_NODAL:
                    type_data = dbmsh.DFLT_FIELDS_NODES_OPEN_CLOSE
                elif it_f[config_mesh.DFLT_FIELD_TYPE] == config_mesh.DFLT_FIELD_TYPE_ELEMENT:
                    type_data = dbmsh.DFLT_FIELDS_ELEMS_OPEN_CLOSE
                else:
                    raise ValueError(f"Unknown field type {it_f[config_mesh.DFLT_FIELD_TYPE]}")
                txt = type_data['open']
                self.fhandle.write(f'{txt}\n')
                self.fhandle.write('1\n')  # one string tag
                # the name of the view
                self.fhandle.write(f'"{name_field}"\n')
                self.fhandle.write('1\n')  # one real tag
                self.fhandle.write(f'{list_steps[it_step]:9.4f}\n')  # the time value
                self.fhandle.write('3\n')  # three integer tags
                self.fhandle.write(f'{it_step:d}\n')  # time step value
                # number of components per nodes
                self.fhandle.write(f'{nb_per_entity:d}\n')
                # number of nodal values
                self.fhandle.write(f'{values[it_step].shape[0]:d}\n')
                #
                for i in range(values[it_step].shape[0]):
                    self.fhandle.write(format_spec.format(i + 1, *values[it_step][i, :]))
                txt = type_data['close']
                self.fhandle.write(f'{txt}\n')


class MSHReader:
    """
    MSHReader is a class designed to read and process mesh files in the `.msh` format. 
    It provides functionality to parse nodes, elements, and tags from the file and 
    organize them into structured data for further use.

    Attributes:
        nodes (numpy.ndarray): Array of node coordinates.
        dim (int): Dimension of the mesh (2D or 3D).
        nbNodes (int): Number of nodes in the mesh.
        elems (dict): Dictionary of elements, where keys are element types and values
        are lists of element connectivity.
        tags_list (dict): Dictionary of tags and associated elements.
        fhandle (file object): File handle for the opened `.msh` file.
        obj_file (fileio.fileHandler): File handler object for managing file operations.
        read_data (str): Current section being read ('nodes', 'elems', or None).
        cur_it (int): Current iteration index for reading nodes or elements.

    Methods:
        __init__(filename=None, type='mshv2', dim=3):
            Initializes the MSHReader object, opens the file, and reads its content.

        initcontent():
            Initializes or resets the content attributes of the object.

        __del__():
            Destructor method to clean up the object.

        clean():
            Cleans the object by resetting its content attributes.

        read_nodes(dim=None, line_str=None):
            Reads node data from the `.msh` file.
            Args:
                dim (int, optional): Dimension of the nodes (2D or 3D).
                line_str (str): Content of the current line being read.

        read_elements(line_str=None):
            Reads element data from the `.msh` file.
            Args:
                line_str (str): Content of the current line being read.

        _finalize_elems():
            Finalizes the element data by converting lists to numpy arrays.

        _read_elements_line(arraystr):
            Reads a single line of element data and processes it.
            Args:
                arraystr (list of str): Content of a line for an element.

        get_nodes(tag=None):
            Returns the array of node coordinates.
            Args:
                tag (int, optional): Tag to filter nodes by.

        get_elements(type=None, tag=None, dict_format=True):
            Returns the list of elements.
            Args:
                type (str, optional): Type of elements to filter by.
                tag (int, optional): Tag to filter elements by.
                dict_format (bool, optional): Whether to return elements in dictionary format.

        get_tags():
            Returns the list of tags as integers.

        get_types():
            Returns the list of element types.
    """

    def __init__(self,
                 filename: Union[str, Path, None]=None,
                 file_type: str='mshv2',
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
        self.initcontent()
        _ = file_type
        Logger.debug(f'Open file {filename}')
        # open file and get handle
        self.obj_file = fileio.FileHandler(filename=filename, right='r', safe_mode=False)
        self.fhandle = self.obj_file.get_handler()
        if self.fhandle is None:
            raise ValueError('Unable to open file handle')
        # read file line by line
        for line in cast(Iterable[str], self.fhandle):
            if not self.read_data:
                self.read_data = catch_tag(line)
            elif self.read_data == 'nodes':
                # read nodes
                self.read_nodes(dim, line)
            elif self.read_data == 'elems':
                # read elements
                self.read_elements(line)
        # finalize data
        self._finalize_elems()

        # close file
        self.obj_file.close()

    def initcontent(self)-> None:
        """
        Initializes the content attributes of the mesh object.

        This method sets up the following attributes:
        - `nodes`: An array to store the coordinates of the nodes (initially None).
        - `dim`: The dimension of the mesh (2D or 3D) (initially None).
        - `nbNodes`: The number of nodes in the mesh (initially None).
        - `elems`: A dictionary to store elements, where keys are the names of the elements.
        - `tags_list`: A dictionary to store tags and their associated elements.
        - `fhandle`: A file handle for file operations (initially None).
        - `obj_file`: An object representing the file (initially None).
        - `read_data`: Data read from the file (initially None).
        - `cur_it`: An integer representing the current iteration (initially 0).
        """
        self.nodes = None  # array of nodes coordinates
        self.dim = None  # dimension of the mesh (2/3)
        self.nb_nodes = None  # number of nodes
        self.elems = {}  # dictionary of elements (keys are name of the element)
        self.tags_list = {}  # list of tags and associated elements
        self.fhandle = None
        self.obj_file = None
        self.read_data = None
        self.cur_it = 0

    def __del__(self)-> None:
        """
        Destructor method that is automatically called when the object is about to be destroyed.
        Ensures that any necessary cleanup operations are performed by invoking the `clean` method.
        """
        self.clean()

    def clean(self)-> None:
        """
        Cleans the object by reinitializing its content.

        This method resets the object's state by calling the `initcontent` 
        method, ensuring that any previous data or modifications are cleared.
        """
        self.initcontent()

    def read_nodes(self, dim: Optional[int]=None, line_str: Optional[str]=None)-> None:
        """
        Reads node data from a line in an `.msh` file.

        This method processes the node information from a given line of the file,
        storing the number of nodes, their dimensions, and their coordinates.

        Args:
            dim (Optional[int]): The dimension of the nodes (e.g., 2 for 2D, 3 for 3D).
                                 If not provided, it will be inferred from the data.
            line_str (Optional[str]): The content of the current line being read.

        Behavior:
            - On the first call (`cur_it == 0`), it reads the number of nodes (`nbNodes`)
              and initializes the dimension (`dim`).
            - On subsequent calls, it processes the node coordinates and stores them
              in a NumPy array (`nodes`).
            - Once all nodes are read, it resets the reading state (`read_data` and `cur_it`).

        Attributes:
            nbNodes (int): The total number of nodes to be read.
            dim (int): The dimension of the nodes (e.g., 2D or 3D).
            nodes (np.ndarray): A NumPy array storing the coordinates of the nodes.
            cur_it (int): The current iteration or line being processed.
            read_data (None): A flag indicating the end of the node reading process.

        Logs:
            - Logs the start of the node reading process with the number of nodes.
            - Logs the completion of the node reading process with the total nodes
              and their dimension.
        """
        if line_str is None:
            return
        content_line = line_str.split()
        # first read: access to the number of nodes
        if self.cur_it == 0:
            # read number of nodes
            self.nb_nodes = int(content_line[0])
            self.cur_it += 1
            self.dim = dim
            Logger.debug(f'Start read {self.nb_nodes} nodes')
        else:
            if self.cur_it == 1:
                if not dim:
                    # extract dimension
                    self.dim = len(content_line) - 1
                # create array to store nodes coordinates
                assert self.nb_nodes is not None and self.dim is not None
                self.nodes = np.zeros((self.nb_nodes, self.dim))
            # store nodes
            assert self.nodes is not None and self.dim is not None
            self.nodes[self.cur_it - 1, :] = np.array(content_line[1 : self.dim + 1], dtype=float)
            self.cur_it += 1
            # stop read nodes
            if self.cur_it - 1 == self.nb_nodes:
                self.read_data = None
                self.cur_it = 0
                Logger.debug(f'Nodes read: {self.nb_nodes}, dimension: {self.dim}')

    def read_elements(self, line_str: Optional[str]=None)-> None:
        """
        Reads and processes elements from a given line of input.

        This method is responsible for parsing and storing element connectivity
        information from a line of input. It handles the initialization of the
        number of elements to read, processes each line of element data, and
        finalizes the data once all elements have been read.

        Args:
            line_str (Optional[str]): The content of the current line to be processed.
                                     If None, no processing is performed.

        Behavior:
            - On the first call (self.cur_it == 0), it reads the total number of elements
              from the input line and initializes the reading process.
            - On subsequent calls, it processes the element connectivity data line by line.
            - Once all elements have been read, it finalizes the data, resets internal
              state variables, and logs the results.

        Logging:
            - Logs the start of the element reading process.
            - Logs the number and type of elements read.
            - Logs the tags associated with the elements.

        Note:
            This method relies on helper methods `_read_elements_line` and `_finalize_elems`
            to process individual lines and finalize the data, respectively.
        """
        if line_str is None:
            return

        content_line = line_str.split()
        # first read: access to the number of elements
        if self.cur_it == 0:
            # read number of elements
            self.nb_elems = int(content_line[0])
            self.cur_it += 1
            Logger.debug(f'Start read {self.nb_elems} elements')
        else:
            # store elements connectivity
            self._read_elements_line(content_line)
            self.cur_it += 1
            # stop read elements
            if self.cur_it - 1 == self.nb_elems:
                #  finalize data
                self._finalize_elems()
                # reset
                self.read_data = None
                self.cur_it = 0
                Logger.debug(f'Elements read: {self.nb_elems}')
                Logger.debug('Type of elements')
                for key, val in self.elems.items():
                    Logger.debug(f' > {val.shape[0]} {key}')
                Logger.debug('Tags')
                for tag_name, tag_data in self.tags_list.items():
                    Logger.debug(f'Tag: {tag_name}')
                    for key, val in tag_data.items():
                        Logger.debug(f' > {len(val)} {key}')

    def _finalize_elems(self)-> None:
        """
        Finalizes the element data by converting each element in the `elems` dictionary 
        to a NumPy array. This ensures that the data structure is consistent and 
        optimized for numerical operations.

        Returns:
            None
        """
        for it in self.elems:
            self.elems[it] = np.array(self.elems[it])

    def _read_elements_line(self, arraystr: list)-> None:
        """
        Reads and processes a line of element data from a mesh file.

        Args:
            arraystr (list): A list of strings representing the content of a line 
                             for an element in the mesh file.

        Functionality:
            - Converts the input line to an integer array.
            - Extracts the element ID and determines its type using the 
            `dbmsh.get_elem_type_from_msh` function.
            - Retrieves the number of tags and the associated tags from the line.
            - Extracts the nodes associated with the element.
            - Stores the element nodes in the `self.elems` dictionary, categorized by element type.
            - Updates the `self.tags_list` dictionary to associate tags with their corresponding 
            elements and element types.

        Notes:
            - The `self.elems` dictionary organizes elements by their type, with each type 
            containing a list of node arrays.
            - The `self.tags_list` dictionary maps tags (as strings) to a nested structure 
            of element types and their corresponding indices in `self.elems`.

        Raises:
            ValueError: If the input line does not conform to the expected format or contains 
            invalid data.
        """
        # convert to int
        arrayint = np.array(arraystr, dtype=int)
        # get element id
        element_id = arrayint[1]
        elem_type = dbmsh.get_elem_type_from_msh(element_id)
        # get number of tags
        nb_tags = arrayint[2]
        tags = arrayint[3 : 3 + nb_tags]
        # element nodes
        element_nodes = arrayint[3 + nb_tags :]
        # check if element can be stored
        if elem_type not in self.elems:
            self.elems[elem_type] = list()
        # store it
        self.elems[elem_type].append(element_nodes)
        # get the item of the element
        ix = len(self.elems[elem_type]) - 1
        # create the list for each tag
        for it in tags:
            it_s = str(it)
            # check if the tag already exists
            if it_s not in self.tags_list:
                self.tags_list[it_s] = dict()
            # check if the element type has been already created
            if elem_type not in self.tags_list[it_s]:
                self.tags_list[it_s][elem_type] = list()
            # store the elements
            self.tags_list[it_s][elem_type].append(ix)

    def get_nodes(self, tag: Optional[int]=None)-> np.ndarray:
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
        if tag is not None:
            # get elements
            elts = self.get_elements(tag=tag, dict_format=False)
            assert self.nodes is not None
            if not isinstance(elts, np.ndarray):
                return np.array([])
            return self.nodes[np.unique(elts.flatten())-1,:]
        return np.array([]) if self.nodes is None else self.nodes

    def get_elements(self,
                     elem_type: Optional[str|None]=None,
                     tag: Optional[int|None]=None,
                     dict_format: bool=True)-> Union[np.ndarray, dict]:
        """
        Retrieve elements from the mesh based on specified criteria.

        Parameters:
            type (str, optional): The type of elements to retrieve. This can be specified 
                using the Gmsh element ID or the general name of the elements. If not provided, 
                elements of all types will be considered.
            tag (int, optional): The tag to filter elements by. If specified, only elements 
                associated with the given tag will be retrieved. If not provided, elements 
                from all tags will be included.
            dict_format (bool, optional): Determines the format of the returned data. 
                If True, the elements will be returned as a dictionary. If False, the elements 
                will be returned as a NumPy array. Defaults to True.

        Returns:
            Union[np.ndarray, dict]: The retrieved elements. The format depends on the 
            `dict_format` parameter:
                - If `dict_format` is True, a dictionary is returned where keys are element 
                  types and values are NumPy arrays of elements.
                - If `dict_format` is False, a NumPy array of elements is returned. If multiple 
                  element types are present, only the first type is returned with a warning.

        Notes:
            - If `type` is specified, only elements of the given type are retrieved.
            - If `tag` is specified, only elements associated with the given tag are retrieved.
            - If `dict_format` is False and multiple element types are present, only the first 
              type is exported, and a warning is logged.
        """
        elems_tag = dict()
        # filter by tag
        if tag:
            if str(tag) in self.tags_list:
                elems_tag = self.tags_list[str(tag)]
        else:
            # copy all meshes associated to all tags
            # along tags
            for _, vt in self.tags_list.items():
                # along meshes in tag
                for im in vt.keys():
                    # check if element type already exists
                    if im not in elems_tag:
                        elems_tag[im] = list()
                    elems_tag[im].extend(vt[im])
        # filter by type
        if elem_type:
            elems_export = list()
            elems_export_unique = list()
            if elem_type in elems_tag:
                elems_export = self.elems[elem_type][elems_tag[elem_type], :]
                elems_export_unique = np.unique(elems_export, axis=0)
        else:
            elems_export = dict()
            elems_export_unique = dict()
            for key,val in elems_tag.items():
                elems_export[key] = self.elems[key][val, :]
                elems_export_unique[key] = np.unique(elems_export[key], axis=0)

        # specific export
        if not dict_format and not elem_type:
            if not isinstance(elems_export, dict):
                return np.array([])
            if len(elems_export) > 1:
                txt = 'Elements exported without the dictionary format: some data are not exported'
                Logger.warning(txt)
            if len(elems_export) == 0:
                Logger.warning('No element to export')
                return np.array([])
            id_elems = list(elems_export.keys())[0]
            elems_export = elems_export[id_elems]
            elems_export_unique = elems_export_unique[id_elems]

        return cast(Union[np.ndarray, dict], elems_export_unique)

    def get_tags(self)-> list:
        """
        Retrieves the list of tags as integers.

        This method processes the `tags_list` attribute of the object, which is expected 
        to be a dictionary-like structure. It extracts the keys, converts them to integers, 
        and returns them as a list.

        Returns:
            list: A list of integer tags. If `tags_list` is empty or not set, an empty 
            list is returned.
        """
        list_tags = list()
        list_export = list()
        if self.tags_list:
            list_tags = self.tags_list.keys()
            # convert to integer
            for il in list_tags:
                list_export.append(int(il))
        return list_export

    def get_types(self)-> list:
        """
        Retrieve the list of element types (tags) present in the mesh.

        Returns:
            list: A list of integer tags representing the types of elements 
                  in the mesh. If no elements are present, an empty list is returned.
        """
        list_types = list()
        if self.elems:
            list_types = list(self.elems.keys())
        return list_types

    # Backward-compatible method aliases (camelCase)
    def getNodes(self, tag: Optional[int] = None) -> np.ndarray:
        """Compatibility wrapper for :meth:`get_nodes`."""
        return self.get_nodes(tag=tag)

    def getElements(
        self,
        tag: Optional[int] = None,
        type: Optional[Union[str, int]] = None,
        dictFormat: bool = True,
    ) -> Union[np.ndarray, dict]:
        """Compatibility wrapper for :meth:`get_elements`."""
        return self.get_elements(tag=tag, elem_type=type, dict_format=dictFormat)

    def getTags(self) -> list:
        """Compatibility wrapper for :meth:`get_tags`."""
        return self.get_tags()

    def getTypes(self) -> list:
        """Compatibility wrapper for :meth:`get_types`."""
        return self.get_types()


def catch_tag(content: Optional[str|None]=None)-> str|None:
    """
    Determines the type of tag present in the given content.

    This function checks if the provided content matches specific predefined
    tags for "nodes" or "elems" and returns the corresponding tag type.

    Args:
        content (str, optional): The content to check for a tag. Defaults to None.

    Returns:
        str: The type of tag found in the content. Returns 'nodes' if the content
             matches the opening tag for nodes, 'elems' if it matches the opening
             tag for elements, or None if no match is found.
    """
    tag_start_nodes = dbmsh.DFLT_NODES_OPEN_CLOSE['open']
    tag_start_elems = dbmsh.DFLT_ELEMS_OPEN_CLOSE['open']
    type_tag = None
    if content is None:
        return type_tag
    if tag_start_nodes == content.strip():
        type_tag = 'nodes'
    if tag_start_elems == content.strip():
        type_tag = 'elems'
    return type_tag


def check_content_line(content: Optional[list|None]=None,
                       pattern: Optional[str|None]=None,
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
    status = True
    if not content:
        status = False
    if not pattern:
        status = False
    if content is not None and len(content) == 0:
        status = False

    if status and content is not None:
        if content[0] != pattern:
            status = False
    return status

writer = MSHWriter
reader = MSHReader
mshWriter = MSHWriter
mshReader = MSHReader
