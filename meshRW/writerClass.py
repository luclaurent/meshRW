"""
This file is part of the meshRW package
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Union, Optional

import numpy as np
from loguru import logger as Logger

from . import configMESH

class writer(ABC):
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
        binary (bool): Whether to write the file in binary format.
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
        globPhysGrp (int): Global physical group identifier.
        nbCellFields (int): Number of cell-based fields.
        nbPointFields (int): Number of point-based fields.
        nbTemporalFields (int): Number of temporal fields.

    Methods:
        __init__(filename, nodes, elements, fields, append, title, binary, opts):
            Initialize the writer with file and mesh data.

        setOptions(opts):
            Abstract method to set options for the writer.

        getAppend():
            Abstract method to get the append mode.

        adaptTitle(txt, append):
            Adapt the title with additional information.

        writeContents(nodes, elements, fields, numStep):
            Abstract method to write the contents of the mesh.

        writeHeader():
            Write the header to the output file.

        writeNodes(nodes):
            Abstract method to write the nodes.

        writeElements(elements):
            Abstract method to write the elements.

        writeFields(fields, numStep):
            Abstract method to write the fields.

        splitFilename():
            Split the filename into path, basename, and extension.

        getFilename(prefix, suffix, extension):
            Generate a new filename with optional prefix, suffix, and extension.

        logBadExtension():
            Log an error for unsupported file extensions.

        dataAnalysis(nodes, elems, fields):
            Analyze the mesh data, including nodes, elements, and fields.

        fieldAnalysis(fields):
            Analyze the fields, including their types and temporal properties.
    """
    def __init__(        
        self,
        filename: Union[str, Path] = None,
        nodes: Union[list, np.ndarray] = None,
        elements: dict = None,
        fields: Union[list, np.ndarray] = None,
        append: bool = False,
        title: str = None,
        binary: bool = False,
        opts: dict = {},
    )-> None:
        """
        Initialize the writer class with the provided parameters.

        Parameters:
            filename (Union[str, Path], optional): The name of the file to write to. Defaults to None.
            nodes (Union[list, np.ndarray], optional): The list or array of nodes. Defaults to None.
            elements (dict, optional): A dictionary containing element data. Defaults to None.
            fields (Union[list, np.ndarray], optional): The list or array of fields. Defaults to None.
            append (bool, optional): Whether to append to the file if it exists. Defaults to False.
            title (str, optional): The title of the file or dataset. Defaults to None.
            binary (bool, optional): Whether to write the file in binary format. Defaults to False.
            opts (dict, optional): Additional options for the writer. Defaults to an empty dictionary.

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
        self.title = self.adaptTitle(txt=title)
        self.filename = Path(filename)
        self.basename = self.filename.name
        self.binary = binary
        # set options
        self.setOptions(opts)
        #
        self.db = None
        #
        self.nbNodes = 0
        self.nbElems = 0
        #
        self.listPhysGrp = []
        self.nbSteps = 0
        self.steps = []
        self.nbFields = 0        
        # run data analysis
        self.dataAnalysis(nodes, elements, fields)


    @abstractmethod
    def setOptions(self, opts: dict)-> None:
        """
        Set the options for the writer.

        Args:
            opts (dict): A dictionary containing configuration options 
                         to customize the writer's behavior.

        Returns:
            None
        """
        pass


    @abstractmethod
    def getAppend(self)-> None:
        """
        Retrieves the append operation or functionality.

        This method is intended to be implemented to define how data or elements
        should be appended in the context of the class.

        Returns:
            None: This is a placeholder method and does not return any value.
        """
        pass

    def adaptTitle(self, txt: str='', append: bool=False)-> str:
        """
        Adapt the title by appending or replacing it with additional information.

        Args:
            txt (str, optional): The text to append or replace the title with. Defaults to an empty string.
            append (bool, optional): If True, appends `txt` to the existing title. 
                                     If False, replaces the title with `txt`. Defaults to False.

        Returns:
            str: The adapted title. If no text is provided and `append` is False, 
                 the current date and time in the format 'YYYY-MM-DD HH:MM:SS' is returned.
        """
        if append:
            txtFinal = self.title + txt
        else:
            txtFinal = txt
        if not txtFinal:
            txtFinal = datetime.today().strftime('%Y-%M-%d %H:%M:%s')
        return txtFinal

    @abstractmethod
    def writeContents(self, 
                      nodes: Union[list, np.ndarray], 
                      elements: Union[list, np.ndarray], 
                      fields: Optional[dict] = None, 
                      numStep: Optional[int] = None)-> None:
        """
        Writes the contents of the mesh data to a file.

        Args:
            nodes (list): A list of nodes, where each node is represented by its coordinates.
            elements (list): A list of elements, where each element is defined by its connectivity.
            fields (dict, optional): A dictionary containing field data associated with the nodes or elements. 
                         Defaults to None.
            numStep (int, optional): The step number for which the data is being written. Defaults to None.

        Returns:
            None
        """
        pass

    def writeHeader(self)-> None:
        """
        Writes the header section of the mesh file.

        This method is responsible for generating and writing the header
        information required for the mesh file format. The specific details
        of the header depend on the file format being used.

        Returns:
            None
        """
        pass

    @abstractmethod
    def writeNodes(self, nodes: Union[list, np.ndarray]) -> None:
        """
        Writes the given nodes to a file or data structure.

        Args:
            nodes (Union[list, np.ndarray]): A collection of nodes to be written. 
            This can be a list or a NumPy array, where each node typically 
            represents a point or vertex in a mesh.

        Returns:
            None
        """
        pass

    @abstractmethod
    def writeElements(self, elements: Union[list, np.ndarray]) -> None:
        """
        Writes the provided elements to a file or data structure.

        Args:
            elements (Union[list, np.ndarray]): A collection of elements to be written. 
            This can be a list or a NumPy array.

        Returns:
            None
        """
        pass

    @abstractmethod
    def writeFields(self, 
                    fields: Optional[dict] = None, 
                    numStep: Optional[int] = None) -> None:
        """
        Writes the provided fields to a file or data structure.

        Args:
            fields (Optional[dict]): A dictionary containing the fields to be written. 
                         Keys represent field names, and values represent field data.
            numStep (Optional[int]): An optional integer representing the step number 
                         associated with the fields being written.

        Returns:
            None
        """
        pass

    def splitFilename(self)-> tuple:
        """
        Splits the filename into its path, base name, and extension.

        This method extracts the path, base name, and extension of the file 
        associated with the `self.filename` attribute. It iteratively checks 
        if the file extension is allowed based on the `self.db.ALLOWED_EXTENSIONS` 
        list. If the extension is not valid after two iterations, it logs the 
        bad extension using the `self.logBadExtension()` method.

        Returns:
            tuple: A tuple containing:
                - path (Path): The parent directory of the file.
                - filename (str): The base name of the file without the extension.
                - extension (str): The concatenated file extension(s).

        Raises:
            None: This method does not explicitly raise exceptions but relies on 
            the `self.logBadExtension()` method to handle invalid extensions.
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
                self.logBadExtension()
        return path, filename, extension

    def getFilename(self, 
                    prefix: Optional[str] = None, 
                    suffix: Optional[str] = None, 
                    extension: Optional[str] = None) -> str:
        """
        Constructs a filename by optionally adding a prefix, suffix, and/or changing the file extension.

        Args:
            prefix (Optional[str]): A string to prepend to the base filename. Defaults to None.
            suffix (Optional[str]): A string to append to the base filename. Defaults to None.
            extension (Optional[str]): A string to replace the current file extension. Defaults to None.

        Returns:
            str: The modified filename with the specified prefix, suffix, and/or extension.
        """
        path, basename, ext = self.splitFilename()
        if prefix is not None:
            basename = prefix + basename
        if suffix is not None:
            basename = basename + suffix
        if extension is not None:
            ext = extension
        return path / (basename + ext)

    def logBadExtension(self)-> None:
        """
        Logs an error message indicating that the file has a bad extension.

        This method uses the Logger to log an error message specifying the
        filename and the allowed extensions.

        Returns:
            None
        """

        Logger.error('File {}: bad extension (ALLOWED: {})'.format(self.filename, ' '.join(self.db.ALLOWED_EXTENSIONS)))

    def dataAnalysis(self, 
                     nodes: Union[list, np.ndarray], 
                     elems: Union[list, np.ndarray], 
                     fields: Optional[dict] = None)-> None:
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
            globPhysGrp (int): The ID of the global physical group, generated if necessary.
        Logs:
            - Number of nodes.
            - Number of elements.
            - Number of physical groups.
            - Number of elements per type.
            - Number of elements per physical group.
            - Global physical group ID.
        Notes:
            - If no physical groups are provided, an artificial physical group is created.
            - If `fields` is provided, the `fieldAnalysis` method is called to analyze the fields.
        """
        
        self.nbNodes = len(nodes)
        self.nbElems = 0
        #
        self.elemPerType = {}
        self.elemPerGrp = {}
        self.nameGrp = {}
        #
        if isinstance(elems, dict):
            elems = [elems]
        #
        itGrpE = 0
        for e in elems:
            if e.get('type') not in self.elemPerType:
                self.elemPerType[e.get('type')] = 0
            self.elemPerType[e.get('type')] += len(e.get('connectivity'))
            self.nbElems += len(e.get('connectivity'))
            name = e.get('name', f'grp-{itGrpE}')
            itGrpE += 1
            if e.get('physgrp') is not None:
                if not isinstance(e.get('physgrp'), list) or not isinstance(e.get('physgrp'), list):
                    physgrp = [e.get('physgrp')]
                else:
                    physgrp = e.get('physgrp')
                for p in np.unique(physgrp):
                    if p not in self.elemPerGrp:
                        self.elemPerGrp[p] = 0
                    self.elemPerGrp[p] += len(e.get('connectivity'))
                    #
                    if p not in self.nameGrp:
                        self.nameGrp[p] = name
                    else:
                        self.nameGrp[p] += '-' + name
        #
        self.listPhysGrp = list(self.elemPerGrp.keys())
        # generate global physical group
        numinit = configMESH.DFLT_NEW_PHYSGRP_GLOBAL_NUM
        numit = 50
        current = numinit
        while current in self.listPhysGrp:
            current += numit
        self.globPhysGrp = current
        # show stats
        Logger.debug(f'Number of nodes: {self.nbNodes}')
        Logger.debug(f'Number of elements: {self.nbElems}')
        Logger.debug(f'Number of physical groups: {len(self.listPhysGrp)}')
        for t, e in self.elemPerType.items():
            Logger.debug(f'Number of {t} elements: {e}')
        for g in self.listPhysGrp:
            Logger.debug(f'Number of elements in group {g}: {self.elemPerGrp.get(g,0)}')
        Logger.debug(f'Global physical group: {self.globPhysGrp}')
        # create artificial physical group if necessary
        if len(self.listPhysGrp) == 0:
            self.listPhysGrp = [1]
        ## analyse fields
        if fields is not None:
            if isinstance(fields, dict):
                fields = [fields]
            self.fieldAnalysis(fields)

    def fieldAnalysis(self, fields: list)-> None:
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
            self.nbFields (int): Total number of fields.
            self.nbCellFields (int): Number of cell-based fields.
            self.nbPointFields (int): Number of point-based fields.
            self.nbTemporalFields (int): Number of temporal fields.
            self.steps (numpy.ndarray): Array of step indices for temporal fields.
            self.nbSteps (int): Number of steps for temporal fields.

        Logs:
            - Warnings if there are inconsistencies in the step definitions 
              across fields.
            - Debug information about the number of fields and their types.

        Raises:
            None
        """
        """Analyse fields"""
        self.nbFields = len(fields)
        self.nbCellFields = 0
        self.nbPointFields = 0
        self.nbTemporalFields = 0
        itField = -1
        for f in fields:
            itField += 1
            if f.get('type') == 'elemental':
                self.nbCellFields += 1
            elif f.get('type') == 'nodal':
                self.nbPointFields += 1
            if f.get('nbsteps') is not None \
                or f.get('steps') is not None \
                or f.get('timesteps') is not None:
                #
                self.nbTemporalFields += 1
                # load available data
                cSteps = f.get('steps',None)
                cTimeSteps = f.get('timesteps',None)    
                cNbSteps = f.get('nbsteps', None)
                #
                if cNbSteps is None:
                    if cTimeSteps is not None:
                        cNbSteps = len(cTimeSteps)
                    if cSteps is not None:
                        cNbSteps = len(cSteps)
                #
                if cSteps is None:
                    cSteps = np.arange(cNbSteps, dtype=float)
                #
                if cTimeSteps is None:
                    cTimeSteps = cSteps
                # check consistency of definition of steps
                if len(self.steps) > 0:
                    if not np.allclose(self.steps, cSteps):
                        name = f.get('name', f'field-{itField}')
                        Logger.warning(f'Inconsistent steps in fields {name}')
                else:
                    self.steps = cSteps
                    self.nbSteps = cNbSteps

        # show stats
        Logger.debug(f'Number of fields: {self.nbFields}')
        Logger.debug(f'Number of cell fields: {self.nbCellFields}')
        Logger.debug(f'Number of point fields: {self.nbPointFields}')
        Logger.debug(f'Number of temporal fields: {self.nbTemporalFields}')
    
    


def adaptInputs(nodes: Union[list, np.ndarray], 
                elements: Union[list, np.ndarray, dict], 
                fields: Union[list, np.ndarray, dict]=None)-> tuple:
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
    allPhysGrp = []
    for e in elements:
        if e.get('physgrp') is not None:
            allPhysGrp.extend(e.get('physgrp'))
    allPhysGrp = set(allPhysGrp)
    # adapt elements
    if elements is not None:
        if isinstance(elements, dict):
            elements = [elements]
        for e in elements:
            if e.get('connectivity') is not None:
                e['connectivity'] = np.array(e.get('connectivity'))
            if e.get('physgrp',None) is None:
                # manual setting of physical group
                idgrp = getNewPhysGrp(allPhysGrp)
                e['physgrp'] = [idgrp]
                allPhysGrp.add(idgrp)
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

    
def getNewPhysGrp(existing: set)-> int:
    """
    Generate a new physical group ID that does not conflict with existing IDs.

    Args:
        existing (set): A set of integers representing the IDs of existing physical groups.

    Returns:
        int: A new unique physical group ID starting from a default value and incrementing
             until an unused ID is found.
    """
    idtstart = configMESH.DFLT_NEW_PHYSGRP_NUM
    while idtstart in existing:
        idtstart += 1
    return idtstart