"""
This file is part of the meshRW package
---
This class is a part of the meshRW library and will write a msh file from a mesh using gmsh API
----
Luc Laurent - luc.laurent@lecnam.net -- 2024
"""

import time
from pathlib import Path
from typing import Union, Optional
import sys

import gmsh
import numpy as np
from loguru import logger as Logger

from . import dbmsh, various, writerClass


def getViewName(view_tag: int) -> str:
    """
    Retrieves the name of a Gmsh view based on its tag.

    Args:
        view_tag (int): The tag of the Gmsh view.

    Returns:
        str: The name of the Gmsh view associated with the given tag.

    Note:
        This function uses the Gmsh API to fetch the view name. Ensure that
        the Gmsh Python API is properly initialized before calling this function.
    """
    return gmsh.option.getString(f'View[{gmsh.view.getIndex(view_tag)}].Name')


class mshWriter(writerClass.writer):
    """
    mshWriter is a class for writing mesh files using the Gmsh API. It provides functionality to write nodes, elements, 
    and fields into a Gmsh-compatible `.msh` file format. The class supports both ASCII and binary formats and allows 
    for appending data to existing files.
    Attributes:
        itName (int): Iterator for naming fields.
        db (module): Database module for mesh-related operations.
        title (str): Title of the mesh file.
        modelName (str): Name of the Gmsh model.
        globEntity (dict): Dictionary of global entities for each dimension.
        entities (dict): Dictionary of physical groups and their associated entities.
        nbNodes (int): Number of nodes in the mesh.
        nbElems (int): Number of elements in the mesh.
    Methods:
        __init__(filename, nodes, elements, fields, append, title, verbose, binary, opts):
            Initializes the mshWriter object and writes the contents of the mesh file.
        getAppend():
            Returns the append flag, indicating whether to append data to an existing file.
        setOptions(options):
            Sets default options for the writer, such as the Gmsh version.
        writeContents(nodes, elements, fields):
            Writes the contents of the mesh file, including nodes, elements, and fields.
        writeNodes(nodes):
            Writes the node coordinates to the mesh file.
        writeElements(elements):
            Writes the elements and their connectivity to the mesh file.
        writeFields(fields):
            Writes all fields (nodal or elemental) to the mesh file.
        writeField(field):
            Writes a single field (nodal or elemental) to the mesh file.
        writeFiles():
            Writes the mesh and field data to the `.msh` file, handling binary and ASCII formats.
    Usage:
        This class is designed to be used for exporting mesh data to Gmsh-compatible files. It supports advanced 
        features like physical groups, field data, and binary file formats. The class relies on the Gmsh Python API 
        for its operations.
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
        binary = False,
        opts: dict = {'version': 2.2},
    )-> None:
        """
        Initialize the mesh object using the Gmsh API.

        Parameters:
            filename (Union[str, Path], optional): The file path for the mesh file. Defaults to None.
            nodes (Union[list, np.ndarray], optional): List or array of nodes. Defaults to None.
            elements (dict, optional): Dictionary of elements. Defaults to None.
            fields (Union[list, np.ndarray], optional): List or array of fields. Defaults to None.
            append (bool, optional): Whether to append to an existing file. Defaults to False.
            title (str, optional): Title of the mesh. Defaults to None.
            verbose (bool, optional): Enable verbose logging. Defaults to False.
            binary (bool, optional): Whether to write the file in binary format. Defaults to False.
            opts (dict, optional): Additional options for the mesh, such as version. Defaults to {'version': 2.2}.

        Attributes:
            itName (int): Iterator for naming.
            db (module): Database module for mesh configurations.
            title (str): Title of the mesh, defaults to 'Imported mesh' if not provided.
            modelName (str): Name of the model, derived from the title.

        Notes:
            - The method adapts the verbosity of the logger based on the `verbose` parameter.
            - Inputs are adapted using the `writerClass.adaptInputs` method.
            - The `writeContents` method is called to write the mesh contents.
        """
        # # adapt verbosity logger
        # if not verbose:
        #     Logger.remove()
        #     Logger.add(sys.stderr, level="INFO") 
        #
        Logger.info('Create msh file using gmsh API')
        self.itName = 0 # name iterators
        # adapt inputs
        nodes, elements, fields = writerClass.adaptInputs(nodes, elements, fields)
        # initialization
        super().__init__(filename, nodes, elements, fields, append, title, binary, opts)
        # load specific configuration
        self.db = dbmsh
        #
        if self.title is None:
            self.title = 'Imported mesh'
        self.modelName = self.title

        # write contents
        self.writeContents(nodes, elements, fields)

    def getAppend(self)-> bool:
        """
        Checks if the append flag is set.

        Returns:
            bool: True if the append flag is set, False otherwise.
        """
        return self.append

    def setOptions(self, options: dict)-> None:
        """
        Sets the options for the object with default values if not provided.

        Args:
            options (dict): A dictionary containing option keys and their values.
            - 'version' (float, optional): The version number to set. Defaults to 2.2.

        Returns:
            None
        """
        self.version = options.get('version', 2.2)

    def writeContents(self, 
                      nodes: Union[list, np.ndarray], 
                      elements: dict, 
                      fields: Optional[Union[list, np.ndarray]]=None)-> None:
        """
        Write the contents of a mesh, including nodes, elements, and optional fields, 
        to a Gmsh-compatible file.
        Args:
            nodes (Union[list, np.ndarray]): A list or numpy array containing the nodes of the mesh.
            elements (dict): A dictionary containing the elements of the mesh, where keys represent 
                element types and values contain the corresponding element data.
            fields (Optional[Union[list, np.ndarray]]): Optional list or numpy array containing 
                field data to be written to the mesh file. Defaults to None.
        Returns:
            None
        This method initializes the Gmsh API, creates physical groups and entities for the mesh, 
        adds nodes and elements, optionally writes field data, and saves the mesh to a file. 
        It also ensures proper cleanup of the Gmsh environment after writing the file.
        """
        # initialize gmsh
        gmsh.initialize()
        gmsh.option.setNumber('Mesh.MshFileVersion', self.version)
        gmsh.option.setNumber('PostProcessing.SaveMesh', 1)  # export mesh when save fields
        # create empty entities
        gmsh.model.add(self.modelName)
        # add global physical group
        self.globEntity = dict()
        # get dimension of all elements
        dimElem = set([self.db.getDim(e.get('type')) for e in elements])
        for d in dimElem:
            self.globEntity[d] = gmsh.model.addDiscreteEntity(d)
            gmsh.model.addPhysicalGroup(d, [self.globEntity[d]], self.globPhysGrp, name='Global')
        self.entities = {}
        # create physical groups for each dimension
        Logger.info(f'Create {len(self.listPhysGrp)} entities for physical group')
        for g in self.listPhysGrp:
            self.entities[g] = list()
            for d in range(4):
                self.entities[g].append(gmsh.model.addDiscreteEntity(d))
                gmsh.model.addPhysicalGroup(d, [self.entities[g][-1]], g, name=self.nameGrp.get(g, None))
        
        

        # add nodes
        self.writeNodes(nodes)

        # add elements
        self.writeElements(elements)

        # add fields
        if fields is not None:
            self.writeFields(fields)

        # run internal gmsh function to reclassify nodes
        gmsh.model.mesh.reclassifyNodes()

        # write msh file
        self.writeFiles()
        # clean gmsh
        gmsh.finalize()

    @various.timeit('Nodes declared')
    def writeNodes(self, nodes: Union[list, np.ndarray])-> None:
        """
        Writes the coordinates of nodes to the mesh.

        Parameters:
        -----------
        nodes : Union[list, np.ndarray]
            A list or numpy array containing the coordinates of the nodes to be written.

        Notes:
        ------
        - If the input `nodes` is a list, it will be converted to a numpy array.
        - The number of nodes (`nbNodes`) is determined from the shape of the input array.
        - Node numbering starts from 1 and is sequentially assigned.
        - Nodes are added to the first volume entity in the physical group list (`listPhysGrp`).
        - Uses the Gmsh API to add nodes to the mesh.

        Raises:
        -------
        - Ensure that `self.listPhysGrp` and `self.entities` are properly initialized before calling this method.
        write nodes coordinates
        """
        # adapt nodes
        if isinstance(nodes, list):
            nodes = np.array(nodes)
        #
        self.nbNodes = nodes.shape[0]
        Logger.debug(f'Write {self.nbNodes} nodes')
        #
        nodesNum = np.arange(1, len(nodes) + 1)
        numFgrp = self.listPhysGrp[0]
        # add nodes to first volume entity
        gmsh.model.mesh.addNodes(3, self.entities[numFgrp][-1], nodesNum, nodes.flatten())

    @various.timeit('Elements declared')
    def writeElements(self, elements: Union[list, dict])-> None:
        """
        Writes elements to the mesh model.

        Parameters:
        -----------
        elements : Union[list, dict]
            A list or dictionary containing element connectivity and type information. 
            The input can be in one of the following formats:
            - List of dictionaries:
              [{'connectivity': table1, 'type': eltype1, 'physgrp': grp1}, 
               {'connectivity': table2, 'type': eltype2, 'physgrp': grp2}, ...]
            - Single dictionary:
              {'connectivity': table1, 'type': eltype1, 'physgrp': grp1}

            Keys:
            - 'connectivity': ndarray or list
                The connectivity array defining the elements.
            - 'type': str or int
                The type of elements (refer to `getGmshElemType` and Gmsh documentation for valid types).
            - 'physgrp' (optional): int, list, or ndarray
                Physical group(s) associated with the elements. Can be a single integer or an array of integers.

        Notes:
        ------
        - If `elements` is provided as a dictionary, it is converted to a list internally.
        - Logs the number of elements being added and their types.
        - Adds elements to the Gmsh model using `gmsh.model.mesh.addElementsByType`.
        - If physical groups are specified, elements are also added to the corresponding physical groups.

        Raises:
        -------
        - Any exceptions raised by the Gmsh API during the addition of elements.
        """
        
        # convert to list if dict
        if type(elements) is dict:
            elemsRun = [elements]
        else:
            elemsRun = elements
        #
        Logger.info(f'Add {self.nbElems} elements')
        for m in elemsRun:
            # get connectivity data
            typeElem = m.get('type')
            connectivity = m.get('connectivity')
            physgrp = m.get('physgrp', None)
            codeElem = self.db.getMSHElemType(typeElem)
            dimElem = self.db.getDim(typeElem)
            #
            Logger.info(f'Set {len(connectivity)} elements of type {typeElem}')
            gmsh.model.mesh.addElementsByType(self.globEntity[dimElem], codeElem, [], connectivity.flatten())
            if physgrp is not None:
                if not isinstance(physgrp, np.ndarray) and not isinstance(physgrp, list):
                    physgrp = [physgrp]
                for p in physgrp:
                    gmsh.model.mesh.addElementsByType(self.entities[p][dimElem-1], codeElem, [], connectivity.flatten())

    @various.timeit('Fields declared')
    def writeFields(self, fields: Union[list, np.ndarray])-> None:
        """
        Writes one or more fields to the appropriate output.

        Args:
            fields (Union[list, np.ndarray]): A single field or a list of fields to be written. 
                If a single field is provided as a numpy array, it will be converted into a list.

        Returns:
            None

        Notes:
            - Logs the number of fields being added.
            - Each field is written using the `writeField` method.
        """
        if not isinstance(fields, list):
            fields = [fields]
        Logger.info(f'Add {len(fields)} fields')
        for f in fields:
            self.writeField(f)

    def writeField(self, field: dict)-> None:
        """
        Writes a field to a Gmsh view.
        Parameters:
            field (dict): A dictionary containing the field data with the following keys:
                - 'data' (list or np.ndarray): The field data values. If multiple steps are present, 
                  this should be a list or a 2D array where each row corresponds to a step.
                - 'name' (str, optional): The name of the field. If not provided, a default name 
                  will be generated based on the field type and an internal counter.
                - 'numEntities' (np.ndarray, optional): The entity tags (e.g., node or element IDs) 
                  associated with the field data. If not provided, it defaults to all nodes or elements.
                - 'nbsteps' (int, optional): The number of time steps. If not provided, it will be 
                  inferred from 'steps' or 'timesteps'.
                - 'steps' (list or np.ndarray, optional): The step indices. If not provided, it defaults 
                  to a range from 0 to 'nbsteps'.
                - 'timesteps' (list or np.ndarray, optional): The time values corresponding to each step. 
                  If not provided, it defaults to zeros.
                - 'dim' (int, optional): The dimensionality of the field data. Defaults to 0.
                - 'type' (str): The type of the field, either 'nodal' or 'elemental'.
        Raises:
            ValueError: If 'typeField' is not 'nodal' or 'elemental'.
        Notes:
            - For 'nodal' fields, the data is associated with nodes, and 'numEntities' defaults to 
              all node IDs.
            - For 'elemental' fields, the data is associated with elements, and 'numEntities' defaults 
              to all element IDs.
            - The function uses Gmsh's API to add the field data to a view, with support for multiple 
              time steps.
        """
        
        # load field data
        data = field.get('data')
        name = field.get('name')
        numEntities = field.get('numEntities', None)
        nbsteps = field.get('nbsteps', None)
        steps = field.get('steps', None)
        timesteps = field.get('timesteps', None)
        dim = field.get('dim', 0)
        typeField = field.get('type')
        #
        if not name:
            name = f'{typeField}_{self.itName}'
            self.itName += 1
            
        # manage steps
        if steps is not None:
            nbsteps = len(steps)
        if timesteps is not None:
            nbsteps = len(timesteps)
        if nbsteps is None:
            nbsteps = 1
        #
        if not steps:
            steps = np.arange(nbsteps, dtype=int)
        if not timesteps:
            timesteps = np.zeros(nbsteps)
        if nbsteps == 1 and len(data) > 1:
            data = [data]
        else:
            if len(data) != nbsteps:
                data = np.array(data).transpose()

        # add field
        if typeField == 'nodal':
            nameTypeData = 'NodeData'
            if numEntities is None:
                numEntities = np.arange(1, self.nbNodes + 1)

        elif typeField == 'elemental':
            nameTypeData = 'ElementData'
            if numEntities is None:
                numEntities = np.arange(1, self.nbElems + 1)
        else:
            raise ValueError('typeField must be nodal or elemental')
        #
        tagView = gmsh.view.add(name)
        for s, t in zip(steps, timesteps):
            dataView = data[s]
            if len(dataView.shape) == 1:
                dataView = dataView.reshape((-1, 1))
            gmsh.view.addModelData(tag=tagView, 
                                   step=s, 
                                   modelName=self.modelName, 
                                   dataType=nameTypeData, 
                                   tags=numEntities, 
                                   data=dataView,
                                   time=t)
            # ,
            # numComponents=dim,
            # partition=0)

    @various.timeit('File(s) written')
    def writeFiles(self)-> None:
        """
        Writes mesh and field data to files with advanced options for binary format 
        and appending field data.

        This method handles exporting mesh data and associated fields using the Gmsh 
        API. Depending on the configuration, it can write data in binary or ASCII 
        format, append field data to the same file, or save each field in separate files.

        Attributes:
            binary (bool): Determines whether the mesh is written in binary format.
            filename (Path): The base filename for saving the mesh and field data.
            getAppend (Callable): A method that returns a boolean indicating whether 
                to append field data to the same file.
            getFilename (Callable): A method that generates a new filename with a 
                specified suffix.

        Behavior:
            - If `binary` is True, the mesh is written in binary format; otherwise, 
              it is written in ASCII format.
            - If `getAppend()` returns True, all fields are appended to the same file.
            - If `getAppend()` returns False, each field is saved in a separate file 
              with a unique suffix.

        Logging:
            - Logs the name of each field saved, the size of the file, and the time 
              taken to save the data.

        Raises:
            Any exceptions raised by the Gmsh API during file writing.

        Notes:
            - Field names longer than 15 characters are truncated.
            - Spaces in field names are replaced with underscores.
        """
        if self.binary:
            gmsh.option.setNumber('Mesh.Binary', 1)
        else:
            gmsh.option.setNumber('Mesh.Binary', 0)
        gmsh.write(self.filename.as_posix())
        if self.getAppend():
            for t in gmsh.view.getTags():
                viewname = getViewName(t)
                starttime = time.perf_counter()
                gmsh.view.write(t, self.filename.as_posix(), append=True)
                Logger.info(
                    f'Field {viewname} save in {self.filename} ({various.convert_size(self.filename.stat().st_size)})'
                )
        else:
            it = 0
            for t in gmsh.view.getTags():
                viewname = getViewName(t)
                viewname = viewname.replace(' ', '_')
                if len(viewname) > 15:
                    viewname = viewname[0:15]
                #
                newfilename = self.getFilename(suffix=f'_view-{it}_{viewname}')
                starttime = time.perf_counter()
                gmsh.view.write(t, newfilename.as_posix(), append=False)
                Logger.info(
                    f'Data save in {newfilename} ({various.convert_size(newfilename.stat().st_size)}) - Elapsed {(time.perf_counter()-starttime):.4f} s'
                )

    # def dataAnalysis(self,nodes,elems,fields):
    #     """ """
    #     self.nbNodes = len(nodes)
    #     self.nbElems = 0
    #     #
    #     self.elemPerType = {}
    #     self.elemPerGrp = {}
    #     self.nameGrp = {}
    #     #
    #     if isinstance(elems,dict):
    #         elems = [elems]
    #     #
    #     itGrpE = 0
    #     for e in elems:
    #         if e.get('type') not in self.elemPerType:
    #             self.elemPerType[e.get('type')] = 0
    #         self.elemPerType[e.get('type')] += len(e.get('connectivity'))
    #         self.nbElems += len(e.get('connectivity'))
    #         name = e.get('name','grp-{}'.format(itGrpE))
    #         itGrpE += 1
    #         if e.get('physgrp') is not None:
    #             if not isinstance(e.get('physgrp'),list) or not isinstance(e.get('physgrp'),list):
    #                 physgrp = [e.get('physgrp')]
    #             else:
    #                 physgrp = e.get('physgrp')
    #             for p in np.unique(physgrp):
    #                 if p not in self.elemPerGrp:
    #                     self.elemPerGrp[p] = 0
    #                 self.elemPerGrp[p] += len(e.get('connectivity'))
    #                 #
    #                 if p not in self.nameGrp:
    #                     self.nameGrp[p] = name
    #                 else:
    #                     self.nameGrp[p] += '-' + name
    #     #
    #     self.listPhysGrp = list(self.elemPerGrp.keys())
    #     # generate global physical group
    #     numinit = 1000
    #     numit = 50
    #     current = numinit
    #     while current in self.listPhysGrp:
    #         current += numit
    #     self.globPhysGrp = current
    #     # show stats
    #     Logger.debug('Number of nodes: {}'.format(self.nbNodes))
    #     Logger.debug('Number of elements: {}'.format(self.nbElems))
    #     Logger.debug('Number of physical groups: {}'.format(len(self.listPhysGrp)))
    #     for t,e in self.elemPerType.items():
    #         Logger.debug('Number of {} elements: {}'.format(t,e))
    #     for g in self.listPhysGrp:
    #         Logger.debug('Number of elements in group {}: {}'.format(g,self.elemPerGrp.get(g,0)))
    #     Logger.debug('Global physical group: {}'.format(self.globPhysGrp))
    #     # create artificial physical group if necessary
    #     if len(self.listPhysGrp) == 0:
    #         self.listPhysGrp = [1]
