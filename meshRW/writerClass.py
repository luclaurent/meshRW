"""
This file is part of the meshRW package
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Union, Optional

import numpy as np
from loguru import logger as Logger

from . import config_mesh

class Writer(ABC):
    """
    Abstract base class for writing mesh data to files.

    This class provides a framework for writing mesh data, including nodes, elements, 
    and fields, to a file. It includes methods for setting options, analyzing data, 
    and writing various components of the mesh. Subclasses must implement the 
    abstract methods to define specific behavior for different file formats.

    Attributes:
        append (bool): Whether to append to an existing file.
        title (str): Title of the file, adapted with additional information if needed.
        filename (Path): Path to the output file.
        basename (str): Base name of the output file.
        db: Database object for managing allowed extensions.
        nbNodes (int): Number of nodes in the mesh.
        nbElems (int): Number of elements in the mesh.
        listPhysGrp (list): List of physical groups in the mesh.
        nbSteps (int): Number of time steps in the fields.
        steps (list): List of time steps.
        nbFields (int): Number of fields in the mesh.
        elemPerType (dict): Dictionary mapping element types to their counts.
        elemPerGrp (dict): Dictionary mapping physical groups to their element counts.
        nameGrp (dict): Dictionary mapping physical group IDs to their names.
        glob_phys_grp (int): Global physical group identifier.
        nbCellFields (int): Number of cell-based fields.
        nbPointFields (int): Number of point-based fields.
        nbTemporalFields (int): Number of temporal fields.

    Methods:
        __init__(filename, nodes, elements, fields, append, title, opts):
            Initialize the writer with file and mesh data.

        set_options(opts):
            Abstract method to set options for the writer.

        get_append():
            Abstract method to get the append mode.

        adapt_title(txt, append):
            Adapt the title with additional information.

        write_contents(nodes, elements, fields, num_step):
            Abstract method to write the contents of the mesh.

        write_header():
            Write the header to the output file.

        write_nodes(nodes):
            Abstract method to write the nodes.

        write_elements(elements):
            Abstract method to write the elements.

        write_fields(fields, num_step):
            Abstract method to write the fields.

        split_filename():
            Split the filename into path, basename, and extension.

        get_filename(prefix, suffix, extension):
            Generate a new filename with optional prefix, suffix, and extension.

        log_bad_extension():
            Log an error for unsupported file extensions.

        data_analysis(nodes, elems, fields):
            Analyze the mesh data, including nodes, elements, and fields.

        field_analysis(fields):
            Analyze the fields, including their types and temporal properties.
    """
    def __init__(
        self,
        filename: Union[str, Path, None] = None,
        nodes: Union[list, np.ndarray, None] = None,
        elements: dict|None = None,
        fields: Union[list, np.ndarray, None] = None,
        append: bool = False,
        title: str|None = None,
        opts: dict|None = None,
    )-> None:
        """
        Initialize the writer class with the provided parameters.

        Parameters:
            filename (Union[str, Path], optional): The name of the file to write to. 
            Defaults to None.
            nodes (Union[list, np.ndarray], optional): The list or array of nodes. 
            Defaults to None.
            elements (dict, optional): A dictionary containing element data. 
            Defaults to None.
            fields (Union[list, np.ndarray], optional): The list or array of fields. 
            Defaults to None.
            append (bool, optional): Whether to append to the file if it exists. 
            Defaults to False.
            title (str, optional): The title of the file or dataset. 
            Defaults to None.
            binary (bool, optional): Whether to write the file in binary format. 
            Defaults to False.
            opts (dict, optional): Additional options for the writer. 
            Defaults to an empty dictionary.

        Attributes:
            append (bool): Indicates if the file should be appended.
            title (str): The adapted title of the file or dataset.
            filename (Path): The file path object for the filename.
            basename (str): The base name of the file.
            binary (bool): Indicates if the file is in binary format.
            db (None): Placeholder for database-related functionality.
            nbNodes (int): The number of nodes.
            nbElems (int): The number of elements.
            listPhysGrp (list): A list of physical groups.
            nbSteps (int): The number of steps.
            steps (list): A list of steps.
            nbFields (int): The number of fields.

        Notes:
            This method also performs data analysis on the provided nodes, elements, and fields.
        """
        self.append = append
        self.title = self.adapt_title(txt=title)
        if filename is not None:
            self.filename = Path(filename)
        else:
            Logger.error('No filename provided')
        self.basename = self.filename.name
        # set options
        self.set_options(opts)
        #
        self.db = None
        #
        self.nb_nodes = 0
        self.nb_elems = 0
        #
        self.list_phys_grp = []
        self.nb_steps = 0
        self.steps = []
        self.nb_fields = 0
        self.nb_cellfields = 0
        self.nb_pointfields = 0
        self.nb_temporalfields = 0
        # run data analysis
        self.data_analysis(nodes, elements, fields)
        # check path exists
        self.check_path(self.filename.parent)

    # Backward-compatible attribute aliases (camelCase)
    @property
    def nbNodes(self) -> int:
        return self.nb_nodes

    @nbNodes.setter
    def nbNodes(self, value: int) -> None:
        self.nb_nodes = value

    @property
    def nbElems(self) -> int:
        return self.nb_elems

    @nbElems.setter
    def nbElems(self, value: int) -> None:
        self.nb_elems = value

    @property
    def listPhysGrp(self) -> list:
        return self.list_phys_grp

    @listPhysGrp.setter
    def listPhysGrp(self, value: list) -> None:
        self.list_phys_grp = value

    @property
    def nbSteps(self) -> int:
        return self.nb_steps

    @nbSteps.setter
    def nbSteps(self, value: int) -> None:
        self.nb_steps = value

    @property
    def nbFields(self) -> int:
        return self.nb_fields

    @nbFields.setter
    def nbFields(self, value: int) -> None:
        self.nb_fields = value

    @property
    def nbCellFields(self) -> int:
        return self.nb_cellfields

    @nbCellFields.setter
    def nbCellFields(self, value: int) -> None:
        self.nb_cellfields = value

    @property
    def nbPointFields(self) -> int:
        return self.nb_pointfields

    @nbPointFields.setter
    def nbPointFields(self, value: int) -> None:
        self.nb_pointfields = value

    @property
    def nbTemporalFields(self) -> int:
        return self.nb_temporalfields

    @nbTemporalFields.setter
    def nbTemporalFields(self, value: int) -> None:
        self.nb_temporalfields = value

    @property
    def elemPerType(self) -> dict:
        return self.elem_per_type

    @elemPerType.setter
    def elemPerType(self, value: dict) -> None:
        self.elem_per_type = value

    @property
    def elemPerGrp(self) -> dict:
        return self.elem_per_grp

    @elemPerGrp.setter
    def elemPerGrp(self, value: dict) -> None:
        self.elem_per_grp = value

    @property
    def nameGrp(self) -> dict:
        return self.name_grp

    @nameGrp.setter
    def nameGrp(self, value: dict) -> None:
        self.name_grp = value

    # Backward-compatible method aliases (camelCase)
    def adaptTitle(self, txt: str | None = '', append: bool = False) -> str:
        """Compatibility wrapper for :meth:`adapt_title`."""
        return self.adapt_title(txt=txt, append=append)

    def checkPath(self, path: Path) -> None:
        """Compatibility wrapper for :meth:`check_path`."""
        self.check_path(path)

    def getFilename(self, extension: str = '', suffix: str = '') -> Path:
        """Compatibility wrapper for :meth:`get_filename`."""
        return self.get_filename(extension=extension, suffix=suffix)

    def dataAnalysis(
        self,
        nodes: Union[list, np.ndarray],
        elems: Union[list, np.ndarray, dict],
        fields: Optional[Union[list, np.ndarray]] = None,
    ) -> None:
        """Compatibility wrapper for :meth:`data_analysis`."""
        self.data_analysis(nodes, elems, fields)

    def fieldAnalysis(self, fields: list) -> None:
        """Compatibility wrapper for :meth:`field_analysis`."""
        self.field_analysis(fields)


    @abstractmethod
    def set_options(self, opts: dict)-> None:
        """
        Set the options for the writer.

        Args:
            opts (dict): A dictionary containing configuration options 
                         to customize the writer's behavior.

        Returns:
            None
        """
        self.opts = opts


    @abstractmethod
    def get_append(self)-> None:
        """
        Retrieves the append operation or functionality.

        This method is intended to be implemented to define how data or elements
        should be appended in the context of the class.

        Returns:
            None: This is a placeholder method and does not return any value.
        """


    def adapt_title(self, txt: str|None='', append: bool=False)-> str:
        """
        Adapt the title by appending or replacing it with additional information.

        Args:
            txt (str, optional): The text to append or replace the title with. 
            Defaults to an empty string.
            append (bool, optional): If True, appends `txt` to the existing title. 
                                     If False, replaces the title with `txt`. Defaults to False.

        Returns:
            str: The adapted title. If no text is provided and `append` is False, 
                 the current date and time in the format 'YYYY-MM-DD HH:MM:SS' is returned.
        """
        if append and txt is not None:
            txt_final = self.title + txt
        else:
            txt_final = txt
        if not txt_final:
            txt_final = datetime.today().strftime('%Y-%M-%d %H:%M:%s')
        return txt_final

    def check_path(self, path: Path)-> None:
        """
        Check if the specified path exists, and create it if it does not.

        Args:
            path (Path): The path to check and potentially create.
        """
        status = path.exists()
        if self.opts.get('createPath', True):
            if not status:
                path.mkdir(parents=True, exist_ok=True)
                Logger.info(f'Path {path} created')
        return status

    @abstractmethod
    def write_contents(self,
                      nodes: Union[list, np.ndarray, None],
                      elements: Union[list, np.ndarray, None],
                      fields: Optional[dict|None] = None,
                      num_step: Optional[int|None] = None)-> None:
        """
        Writes the contents of the mesh data to a file.

        Args:
            nodes (list): A list of nodes, where each node is represented by its coordinates.
            elements (list): A list of elements, where each element is defined by its connectivity.
            fields (dict, optional): A dictionary containing field data associated 
            with the nodes or elements. Defaults to None.
            num_step (int, optional): The step number for which the data is being written. 
            Defaults to None.

        Returns:
            None
        """


    def write_header(self)-> None:
        """
        Writes the header section of the mesh file.

        This method is responsible for generating and writing the header
        information required for the mesh file format. The specific details
        of the header depend on the file format being used.

        Returns:
            None
        """


    @abstractmethod
    def write_nodes(self, nodes: Union[list, np.ndarray]) -> None:
        """
        Writes the given nodes to a file or data structure.

        Args:
            nodes (Union[list, np.ndarray]): A collection of nodes to be written. 
            This can be a list or a NumPy array, where each node typically 
            represents a point or vertex in a mesh.

        Returns:
            None
        """


    @abstractmethod
    def write_elements(self, elements: Union[list, np.ndarray]) -> None:
        """
        Writes the provided elements to a file or data structure.

        Args:
            elements (Union[list, np.ndarray]): A collection of elements to be written. 
            This can be a list or a NumPy array.

        Returns:
            None
        """


    @abstractmethod
    def write_fields(self,
                    fields: Optional[dict] = None,
                    num_step: Optional[int] = None) -> None:
        """
        Writes the provided fields to a file or data structure.

        Args:
            fields (Optional[dict]): A dictionary containing the fields to be written. 
                         Keys represent field names, and values represent field data.
            num_step (Optional[int]): An optional integer representing the step number 
                         associated with the fields being written.

        Returns:
            None
        """


    def split_filename(self)-> tuple:
        """
        Splits the filename into its path, base name, and extension.

        This method extracts the path, base name, and extension of the file 
        associated with the `self.filename` attribute. It iteratively checks 
        if the file extension is allowed based on the `self.db.ALLOWED_EXTENSIONS` 
        list. If the extension is not valid after two iterations, it logs the 
        bad extension using the `self.log_bad_extension()` method.

        Returns:
            tuple: A tuple containing:
                - path (Path): The parent directory of the file.
                - filename (str): The base name of the file without the extension.
                - extension (str): The concatenated file extension(s).

        Raises:
            None: This method does not explicitly raise exceptions but relies on 
            the `self.log_bad_extension()` method to handle invalid extensions.
        """
        extension = ''
        filename = self.filename
        it = 0
        while it < 2:
            path = self.filename.parent
            filename = self.filename.stem
            ext = self.filename.suffix
            extension += ext
            if extension in self.db.ALLOWED_EXTENSIONS:
                it = 3
            else:
                it += 1
            if it == 2:
                self.log_bad_extension()
        return path, filename, extension

    def get_filename(self,
                    prefix: Optional[str] = None,
                    suffix: Optional[str] = None,
                    extension: Optional[str] = None) -> str:
        """
        Constructs a filename by optionally adding a prefix, suffix, 
        and/or changing the file extension.

        Args:
            prefix (Optional[str]): A string to prepend to the base filename. 
            Defaults to None.
            suffix (Optional[str]): A string to append to the base filename. 
            Defaults to None.
            extension (Optional[str]): A string to replace the current file extension. 
            Defaults to None.

        Returns:
            str: The modified filename with the specified prefix, suffix, and/or extension.
        """
        path, basename, ext = self.split_filename()
        if prefix is not None:
            basename = prefix + basename
        if suffix is not None:
            basename = basename + suffix
        if extension is not None:
            ext = extension
        return path / (basename + ext)

    def log_bad_extension(self)-> None:
        """
        Logs an error message indicating that the file has a bad extension.

        This method uses the Logger to log an error message specifying the
        filename and the allowed extensions.

        Returns:
            None
        """
        txt = f"File {self.filename}: bad extension"
        txt += f" (ALLOWED: {' '.join(self.db.ALLOWED_EXTENSIONS)})"
        Logger.error(txt)

    def data_analysis(self,
                     nodes: Union[list, np.ndarray, None],
                     elems: Union[list, np.ndarray, None],
                     fields: Optional[dict|None] = None)-> None:
        """
        Analyzes the provided mesh data, including nodes, elements, and optional fields.
        This method computes various statistics about the mesh, such as the number of nodes,
        elements, element types, and physical groups. It also generates a global physical
        group if necessary and logs the analysis results.
        Args:
            nodes (Union[list, np.ndarray]): A list or numpy array of nodes in the mesh.
            elems (Union[list, np.ndarray]): A list, numpy array, or dictionary of elements
                in the mesh. If a dictionary is provided, it should contain keys such as
                'type', 'connectivity', 'name', and 'physgrp'.
            fields (Optional[dict]): Optional dictionary or list of dictionaries containing
                field data associated with the mesh.
        Attributes:
            nbNodes (int): The total number of nodes in the mesh.
            nbElems (int): The total number of elements in the mesh.
            elemPerType (dict): A dictionary mapping element types to their counts.
            elemPerGrp (dict): A dictionary mapping physical group IDs to the number of
                elements in each group.
            nameGrp (dict): A dictionary mapping physical group IDs to their names.
            listPhysGrp (list): A list of unique physical group IDs in the mesh.
            glob_phys_grp (int): The ID of the global physical group, generated if necessary.
        Logs:
            - Number of nodes.
            - Number of elements.
            - Number of physical groups.
            - Number of elements per type.
            - Number of elements per physical group.
            - Global physical group ID.
        Notes:
            - If no physical groups are provided, an artificial physical group is created.
            - If `fields` is provided, the `field_analysis` method is called to analyze the fields.
        """

        self.nb_nodes = len(nodes)
        self.nb_elems = 0
        #
        self.elem_per_type = {}
        self.elem_per_grp = {}
        self.name_grp = {}
        #
        if isinstance(elems, dict):
            elems = [elems]
        #
        it_grp_e = 0
        for e in elems:
            if e.get('type') not in self.elem_per_type:
                self.elem_per_type[e.get('type')] = 0
            self.elem_per_type[e.get('type')] += len(e.get('connectivity'))
            self.nb_elems += len(e.get('connectivity'))
            name = e.get('name', f'grp-{it_grp_e}')
            it_grp_e += 1
            if e.get('physgrp') is not None:
                if not isinstance(e.get('physgrp'), list) or not isinstance(e.get('physgrp'), list):
                    physgrp = [e.get('physgrp')]
                else:
                    physgrp = e.get('physgrp')
                for p in np.unique(physgrp):
                    if p not in self.elem_per_grp:
                        self.elem_per_grp[p] = 0
                    self.elem_per_grp[p] += len(e.get('connectivity'))
                    #
                    if p not in self.name_grp:
                        self.name_grp[p] = name
                    else:
                        self.name_grp[p] += '-' + name
        #
        self.list_phys_grp = list(self.elem_per_grp.keys())
        # generate global physical group
        numinit = config_mesh.DFLT_NEW_PHYSGRP_GLOBAL_NUM
        numit = 50
        current = numinit
        while current in self.list_phys_grp:
            current += numit
        self.glob_phys_grp = current
        # show stats
        Logger.debug(f'Number of nodes: {self.nb_nodes}')
        Logger.debug(f'Number of elements: {self.nb_elems}')
        Logger.debug(f'Number of physical groups: {len(self.list_phys_grp)}')
        for t, e in self.elem_per_type.items():
            Logger.debug(f'Number of {t} elements: {e}')
        for g in self.list_phys_grp:
            Logger.debug(f'Number of elements in group {g}: {self.elem_per_grp.get(g,0)}')
        Logger.debug(f'Global physical group: {self.glob_phys_grp}')
        # create artificial physical group if necessary
        if len(self.list_phys_grp) == 0:
            self.list_phys_grp = [1]
        ## analyse fields
        if fields is not None:
            if isinstance(fields, dict):
                fields = [fields]
            self.field_analysis(fields)

    def field_analysis(self, fields: list)-> None:
        """
        Analyse the provided fields and compute statistics about them.

        This method processes a list of fields and determines the number of 
        fields, the number of cell-based fields, point-based fields, and 
        temporal fields. It also validates and loads temporal data such as 
        steps and timesteps, ensuring consistency across fields.

        Args:
            fields (list): A list of dictionaries where each dictionary 
                           represents a field. Each field dictionary may 
                           contain the following keys:
                           - 'type': Specifies the type of the field 
                             ('elemental' for cell-based or 'nodal' for 
                             point-based).
                           - 'nbsteps': Number of time steps (optional).
                           - 'steps': Array of step indices (optional).
                           - 'timesteps': Array of time step values (optional).
                           - 'name': Name of the field (optional).

        Attributes Updated:
            self.nb_fields (int): Total number of fields.
            self.nb_cellfields (int): Number of cell-based fields.
            self.nb_pointfields (int): Number of point-based fields.
            self.nb_temporalfields (int): Number of temporal fields.
            self.steps (numpy.ndarray): Array of step indices for temporal fields.
            self.nb_steps (int): Number of steps for temporal fields.

        Logs:
            - Warnings if there are inconsistencies in the step definitions 
              across fields.
            - Debug information about the number of fields and their types.

        Raises:
            None
        """
        #Analyse fields
        self.nb_fields = len(fields)
        self.nb_cellfields = 0
        self.nb_pointfields = 0
        self.nb_temporalfields = 0
        it_field = -1
        for f in fields:
            it_field += 1
            if f.get('type') == 'elemental':
                self.nb_cellfields += 1
            elif f.get('type') == 'nodal':
                self.nb_pointfields += 1
            if f.get('nbsteps') is not None \
                or f.get('steps') is not None \
                or f.get('timesteps') is not None:
                #
                self.nb_temporalfields += 1
                # load available data
                c_steps = f.get('steps',None)
                c_time_steps = f.get('timesteps',None)
                c_nb_steps = f.get('nbsteps', None)
                #
                if c_nb_steps is None:
                    if c_time_steps is not None:
                        c_nb_steps = len(c_time_steps)
                    if c_steps is not None:
                        c_nb_steps = len(c_steps)
                #
                if c_steps is None:
                    c_steps = np.arange(c_nb_steps, dtype=float)
                #
                if c_time_steps is None:
                    c_time_steps = c_steps
                # check consistency of definition of steps
                if len(self.steps) > 0:
                    if not np.allclose(self.steps, c_steps):
                        name = f.get('name', f'field-{it_field}')
                        Logger.warning(f'Inconsistent steps in fields {name}')
                else:
                    self.steps = c_steps
                    self.nb_steps = c_nb_steps

        # show stats
        Logger.debug(f'Number of fields: {self.nb_fields}')
        Logger.debug(f'Number of cell fields: {self.nb_cellfields}')
        Logger.debug(f'Number of point fields: {self.nb_pointfields}')
        Logger.debug(f'Number of temporal fields: {self.nb_temporalfields}')



def adapt_inputs(nodes: Union[list, np.ndarray, None],
                elements: Union[list, np.ndarray, dict],
                fields: Union[list, np.ndarray, dict, None]=None)-> tuple:
    """
    Adapt the input data for the writer by ensuring proper formatting and structure.

    Parameters:
    -----------
    nodes : Union[list, np.ndarray]
        A list or numpy array representing the nodes. If the nodes are in 2D, 
        they will be converted to 3D by appending a zero z-coordinate.
    elements : Union[list, np.ndarray, dict]
        A list, numpy array, or dictionary representing the elements. If a dictionary 
        is provided, it will be wrapped in a list. Physical groups will be assigned 
        if not already present.
    fields : Union[list, np.ndarray, dict], optional
        A list, numpy array, or dictionary representing the fields. If a dictionary 
        is provided, it will be wrapped in a list. Steps and data will be converted 
        to numpy arrays if they are lists. Defaults to None.

    Returns:
    --------
    tuple
        A tuple containing the adapted nodes, elements, and fields.

    Notes:
    ------
    - If `nodes` is None, an error will be logged.
    - If `elements` is None, an error will be logged.
    - If `fields` is None, a warning will be logged.
    - Physical groups for elements will be automatically assigned if missing.
    """
    # adapt nodes
    if nodes is not None:
        if isinstance(nodes, list):
            nodes = np.array(nodes)
        # fix size in case of 2D nodes array
        if nodes.shape[1] == 2:
            nodes = np.hstack((nodes, np.zeros((nodes.shape[0],1))))
    else:
        Logger.error('No nodes provided')
    # adapt elements
    if isinstance(elements, dict):
        elements = [elements]
    # get all physical groups
    all_phys_grp = []
    for e in elements:
        if e.get('physgrp') is not None:
            all_phys_grp.extend(e.get('physgrp'))
    all_phys_grp = set(all_phys_grp)
    # adapt elements
    if elements is not None:
        if isinstance(elements, dict):
            elements = [elements]
        for e in elements:
            if e.get('connectivity') is not None:
                e['connectivity'] = np.array(e.get('connectivity'))
            if e.get('physgrp',None) is None:
                # manual setting of physical group
                idgrp = get_new_phys_grp(all_phys_grp)
                e['physgrp'] = [idgrp]
                all_phys_grp.add(idgrp)
    else:
        Logger.error('No elements provided')
    # adapt fields
    if fields is not None:
        if isinstance(fields, dict):
            fields = [fields]
        for f in fields:
            if f.get('steps') is not None:
                f['steps'] = np.array(f.get('steps'))
            if f.get('data') is not None:
                if isinstance(f.get('data'), list):
                    f['data'] = np.array(f.get('data'))
    else:
        Logger.warning('No fields provided')

    return nodes, elements, fields


def get_new_phys_grp(existing: set)-> int:
    """
    Generate a new physical group ID that does not conflict with existing IDs.

    Args:
        existing (set): A set of integers representing the IDs of existing physical groups.

    Returns:
        int: A new unique physical group ID starting from a default value and incrementing
             until an unused ID is found.
    """
    idtstart = config_mesh.DFLT_NEW_PHYSGRP_NUM
    while idtstart in existing:
        idtstart += 1
    return idtstart


# Backward-compatible module-level aliases (camelCase + legacy class name)
writer = Writer


def adaptInputs(
    nodes: Union[list, np.ndarray, None],
    elements: Union[list, np.ndarray, dict],
    fields: Union[list, np.ndarray, dict, None] = None,
) -> tuple:
    """Compatibility wrapper for :func:`adapt_inputs`."""
    return adapt_inputs(nodes, elements, fields)


def getNewPhysGrp(existing: set) -> int:
    """Compatibility wrapper for :func:`get_new_phys_grp`."""
    return get_new_phys_grp(existing)
