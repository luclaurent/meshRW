"""
This file is part of the meshRW package
---
This class is a part of the meshRW library and will write a msh file from a mesh using gmsh API
----
Luc Laurent - luc.laurent@lecnam.net -- 2024
"""

import time
from pathlib import Path
from typing import Union, Optional, cast

import gmsh
import numpy as np
from loguru import logger as Logger

from . import dbmsh, various, writerclass


def get_view_name(view_tag: int) -> str:
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


class MSHWriter(writerclass.Writer):
    """
    MSHWriter is a class for writing mesh files using the Gmsh API.
    It provides functionality to write nodes, elements, and fields
    into a Gmsh-compatible `.msh` file format. The class supports
    both ASCII and binary formats and allows for appending data to
    existing files.
    Attributes:
        it_name (int): Iterator for naming fields.
        db (module): Database module for mesh-related operations.
        title (str): Title of the mesh file.
        model_name (str): Name of the Gmsh model.
        glob_entity (dict): Dictionary of global entities for each dimension.
        entities (dict): Dictionary of physical groups and their associated entities.
        nb_nodes (int): Number of nodes in the mesh.
        nb_elems (int): Number of elements in the mesh.
    Methods:
        __init__(filename, nodes, elements, fields, append, title, verbose, binary, opts):
            Initializes the MSHWriter object and writes the contents of the mesh file.
        get_append():
            Returns the append flag, indicating whether to append data to an existing file.
        set_options(options):
            Sets default options for the writer, such as the Gmsh version.
        write_contents(nodes, elements, fields):
            Writes the contents of the mesh file, including nodes, elements, and fields.
        write_nodes(nodes):
            Writes the node coordinates to the mesh file.
        write_elements(elements):
            Writes the elements and their connectivity to the mesh file.
        write_fields(fields):
            Writes all fields (nodal or elemental) to the mesh file.
        write_field(field):
            Writes a single field (nodal or elemental) to the mesh file.
        write_files():
            Writes the mesh and field data to the `.msh` file, handling binary 
            and ASCII formats.
    Usage:
        This class is designed to be used for exporting mesh data to Gmsh-compatible files.
        It supports advanced features like physical groups, field data, and binary file formats.
        The class relies on the Gmsh Python API for its operations.
    """

    def __init__(
        self,
        filename: Union[str, Path, None] = None,
        nodes: Union[list, np.ndarray, None] = None,
        elements: dict|None = None,
        fields: Union[list, np.ndarray, None] = None,
        append: bool = False,
        title: str|None = None,
        verbose: bool = False,
        opts: dict|None = None,
    )-> None:
        """
        Initialize the mesh writer object using the Gmsh API.

        Parameters:
            filename (Union[str, Path], optional): The file path for the mesh file. 
            Defaults to None.
            nodes (Union[list, np.ndarray], optional): List or array of node coordinates. 
            Defaults to None.
            elements (dict, optional): Dictionary of element definitions. 
            Defaults to None.
            fields (Union[list, np.ndarray], optional): List or array of fields. 
            Defaults to None.
            append (bool, optional): Whether to append to an existing file. 
            Defaults to False.
            title (str, optional): Title of the mesh. Defaults to None.
            verbose (bool, optional): Enable verbose logging. Defaults to False.
            opts (dict, optional): Additional options for the mesh. Defaults to
                      {'version': 2.2, 'binary': False, 'nodes_reclassify': True, 
                      'createPath': True}.

        Attributes:
            it_name (int): Iterator for naming fields.
            db (module): Database module for mesh configurations.
            title (str): Title of the mesh, defaults to 'Imported mesh' if not provided.
            model_name (str): Name of the model, derived from the title.

        Notes:
            - Inputs are adapted using the `writerClass.adaptInputs` method.
            - The binary option is extracted from the opts dictionary.
            - The `write_contents` method is called to write the mesh contents.
        """
        # # adapt verbosity logger
        # if not verbose:
        #     Logger.remove()
        #     Logger.add(sys.stderr, level="INFO")
        #
        _ = verbose
        Logger.info('Create msh file using gmsh API')
        self.it_name = 0 # name iterators
        # adapt inputs
        if elements is None:
            elements = {}
        adapted_result = writerclass.adapt_inputs(nodes, elements, fields)
        nodes = adapted_result[0]
        elements = adapted_result[1]
        fields = adapted_result[2]
        # initialization
        if opts is None:
            opts = {'version': 2.2, 'binary': False, 'nodes_reclassify': True, 'createPath': True}
        super().__init__(filename, cast(list | np.ndarray, nodes), cast(dict, elements), cast(list | np.ndarray | None, fields), append, title, opts)
        # load specific configuration
        self.db = dbmsh
        self.name_grp: dict = {}  # Initialize name_grp attribute
        #
        if self.title is None:
            self.title = 'Imported mesh'
        self.model_name = self.title

        # write contents
        nodes_cast = cast(list | np.ndarray, nodes)
        elements_cast = cast(dict, elements)
        self.write_contents(nodes_cast, elements_cast, fields)

    def get_append(self)-> bool:
        """
        Checks if the append flag is set.

        Returns:
            bool: True if the append flag is set, False otherwise.
        """
        return self.append

    def set_options(self, opts: dict)-> None:
        """
        Sets the options for the object with default values if not provided.

        Args:
            opts (dict): A dictionary containing option keys and their values.
            - 'version' (float, optional): The version number to set. Defaults to 2.2.

        Returns:
            None
        """
        self.version = opts.get('version', 2.2)
        self.binary = opts.get('binary', False)
        self.nodes_reclassify = opts.get('nodes_reclassify', True)
        self.opts = opts

    def write_contents(self,
                      nodes: Union[list, np.ndarray],
                      elements: dict,
                      fields: Union[list, np.ndarray, None]=None,
                      num_step: Optional[int]=None)-> None:
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
        gmsh.model.add(self.model_name)
        # add global physical group
        self.glob_entity = dict()
        # get dimension of all elements
        dim_elem = set([self.db.get_dim(cast(str, e.get('type'))) for e in cast(list, elements)])
        for d in dim_elem:
            self.glob_entity[d] = gmsh.model.addDiscreteEntity(d)
            gmsh.model.addPhysicalGroup(d, [self.glob_entity[d]], self.glob_phys_grp, name='Global')
        self.entities = {}
        # create physical groups for each dimension
        Logger.info(f'Create {len(self.list_phys_grp)} entities for physical group')
        for g in self.list_phys_grp:
            self.entities[g] = list()
            for d in range(4):
                self.entities[g].append(gmsh.model.addDiscreteEntity(d))
                gmsh.model.addPhysicalGroup(d,
                                            [self.entities[g][-1]],
                                            g,
                                            name=cast(str, self.name_grp.get(g, f'PhysGroup_{g}')))

        # add nodes
        self.write_nodes(nodes)

        # add elements
        self.write_elements(elements)

        # run internal gmsh function to reclassify nodes
        if self.nodes_reclassify:
            Logger.info('Reclassify nodes')
            gmsh.model.mesh.reclassifyNodes()

        # add fields
        if fields is not None:
            self.write_fields(fields)

        # write msh file
        self.write_files()
        # clean gmsh
        gmsh.finalize()

    @various.timeit('Nodes declared')
    def write_nodes(self, nodes: Union[list, np.ndarray])-> None:
        """
        Writes the coordinates of nodes to the mesh.

        Parameters:
        -----------
        nodes : Union[list, np.ndarray]
            A list or numpy array containing the coordinates of the nodes to be
            written.

        Notes:
        ------
        - If the input `nodes` is a list, it will be converted to a numpy array.
        - The number of nodes (`nb_nodes`) is determined from the shape of the
        input array.
        - Node numbering starts from 1 and is sequentially assigned.
        - Nodes are added to the first volume entity in the physical group list
        (`list_phys_grp`).
        - Uses the Gmsh API to add nodes to the mesh.

        Raises:
        -------
        - Ensure that `self.list_phys_grp` and `self.entities` are properly
        initialized before calling this method.
        write nodes coordinates
        """
        # adapt nodes
        if isinstance(nodes, list):
            nodes = np.array(nodes)
        #
        self.nb_nodes = nodes.shape[0]
        Logger.debug(f'Write {self.nb_nodes} nodes')
        #
        nodes_num = np.arange(1, len(nodes) + 1)
        num_fgrp = self.list_phys_grp[0]
        # add nodes to first volume entity
        gmsh.model.mesh.addNodes(3, self.entities[num_fgrp][-1], nodes_num, nodes.flatten())

    @various.timeit('Elements declared')
    def write_elements(self, elements: Union[list, dict])-> None:
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
                The type of elements (refer to `getGmshElemType` and Gmsh documentation
                for valid types).
            - 'physgrp' (optional): int, list, or ndarrayPhysical group(s) associated
            with the elements. Can be a single integer or an array of integers.

        Notes:
        ------
        - If `elements` is provided as a dictionary, it is converted to a list internally.
        - Logs the number of elements being added and their types.
        - Adds elements to the Gmsh model using `gmsh.model.mesh.addElementsByType`.
        - If physical groups are specified, elements are also added to the corresponding
        physical groups.

        Raises:
        -------
        - Any exceptions raised by the Gmsh API during the addition of elements.
        """

        # convert to list if dict
        if isinstance(elements,dict):
            elems_run = [elements]
        else:
            elems_run = elements
        #
        Logger.info(f'Add {self.nb_elems} elements')
        for m in elems_run:
            # get connectivity data
            type_elem = m.get('type')
            connectivity = m.get('connectivity')
            physgrp = m.get('physgrp', None)
            if type_elem is None or connectivity is None:
                raise ValueError('Element must have "type" and "connectivity" keys')
            code_elem = self.db.get_msh_elem_type(type_elem)
            dim_elem = self.db.get_dim(type_elem)
            #
            Logger.info(f'Set {len(connectivity)} elements of type {type_elem}')
            gmsh.model.mesh.addElementsByType(self.glob_entity[dim_elem],
                                              code_elem,
                                              [],
                                              connectivity.flatten())
            if physgrp is not None:
                if not isinstance(physgrp, np.ndarray) and not isinstance(physgrp, list):
                    physgrp = [physgrp]
                for p in physgrp:
                    gmsh.model.mesh.addElementsByType(self.entities[p][dim_elem-1],
                                                      code_elem,
                                                      [],
                                                      connectivity.flatten())

    @various.timeit('Fields declared')
    def write_fields(self, fields: Union[list, np.ndarray, None]=None,
                     num_step: Optional[int]=None)-> None:
        """
        Writes one or more fields to the appropriate output.

        Args:
            fields (Union[list, np.ndarray]): A single field or a list of fields to be written.
                If a single field is provided as a numpy array, it will be converted into a list.

        Returns:
            None

        Notes:
            - Logs the number of fields being added.
            - Each field is written using the `write_field` method.
        """
        if not isinstance(fields, list):
            fields = [fields]
        Logger.info(f'Add {len(fields)} fields')
        for f in fields:
            self.write_field(f, homogeneous=f.get('homogeneous', False))

    def write_field(self, field: dict, homogeneous: bool=False)-> None:
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
            - 'timesteps' (list or np.ndarray, optional): The time values corresponding to each
            step. If not provided, it defaults to zeros.
            - 'dim' (int, optional): The dimensionality of the field data. Defaults to 0.
            - 'type' (str): The type of the field, either 'nodal' or 'elemental'.
            - 'homogeneous' (bool, optional): If True, the field data is treated as homogeneous
              across all entities. Defaults to False.

        Raises:
            ValueError: If 'typeField' is not 'nodal' or 'elemental'.

        Notes:
            - For 'nodal' fields, the data is associated with nodes,
            and 'numEntities' defaults to all node IDs.
            - For 'elemental' fields, the data is associated with elements,
            and 'numEntities' defaults to all element IDs.
            - The function uses Gmsh's API to add the field data to a view,
            with support for multiple time steps.
            - If 'homogeneous' is True, the data is flattened and added using the
              `addHomogeneousModelData` method.
        """

        # load field data
        data = field.get('data')
        name = field.get('name')
        num_entities = field.get('numEntities', None)
        nbsteps = field.get('nbsteps', None)
        steps = field.get('steps', None)
        timesteps = field.get('timesteps', None)
        # dim = field.get('dim', 0)
        type_field = field.get('type')
        #
        if not name:
            name = f'{type_field}_{self.it_name}'
            self.it_name += 1

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
        if data is not None:
            data_len = len(data) if isinstance(data, (list, np.ndarray)) else 0
            if nbsteps == 1 and data_len > 1:
                data = [data]
            else:
                if data_len != nbsteps:
                    data = np.array(data).transpose()
        else:
            data = []

        # add field
        if type_field == 'nodal':
            name_type_data = 'NodeData'
            if num_entities is None:
                num_entities = np.arange(1, self.nb_nodes + 1)

        elif type_field == 'elemental':
            name_type_data = 'ElementData'
            if num_entities is None:
                num_entities = np.arange(1, self.nb_elems + 1)
        else:
            raise ValueError('type_field must be nodal or elemental')
        #
        # in the case of reclassification of the nodes, some of them can be removed
        # filter the input data
        eid = []
        if type_field == 'nodal':
            eid_result = gmsh.model.mesh.getNodes()
            eid = cast(np.ndarray, eid_result[0]) if eid_result else np.array([])
            num_entities_arr = cast(np.ndarray, num_entities)
            if isinstance(eid, np.ndarray) and len(eid) > 0:
                num_entities = num_entities_arr[eid-1]
        tag_view = gmsh.view.add(name)
        for s, t in zip(steps, timesteps):
            if data is None or (isinstance(data, list) and len(data) == 0):
                data_item = None
            else:
                data_item = cast(list, data)[s] if isinstance(data, list) else data[s]
            if data_item is None:
                Logger.warning(f'No data for step {s}')
                continue
            data_view = cast(np.ndarray, data_item)
            # if len(data_view.shape) == 1:
            #     data_view = data_view.reshape((-1, 1))
            # filter data
            if isinstance(eid, np.ndarray) and len(eid) > 0:
                data_view = data_view[eid-1]
            # add homogeneous model data
            if not homogeneous:
                gmsh.view.addModelData(tag=tag_view,
                                    step=s,
                                    modelName=self.model_name,
                                    dataType=name_type_data,
                                    tags=num_entities,
                                    data=data_view if len(data_view.shape) > 1 \
                                        else data_view.reshape(-1, 1),
                                    # in the case of use of addHomogeneousModelData
                                    # (this data must be flatten:
                                    # np.hstack(data_view.transpose()) )
                                    numComponents=data_view.shape[1] if \
                                        len(data_view.shape) > 1 else 1,
                                    time=float(t))
            else:
                gmsh.view.addHomogeneousModelData(tag=tag_view,
                                   step=s,
                                   modelName=self.model_name,
                                   dataType=name_type_data,
                                   tags=num_entities,
                                   data=data_view.flatten() if hasattr(data_view, 'flatten') else np.array(data_view).flatten(),
                                   numComponents=data_view.shape[1] if \
                                       len(data_view.shape) > 1 else 1,
                                   time=float(t))
            # ,
            # numComponents=dim,
            # partition=0)

    @various.timeit('File(s) written')
    def write_files(self)-> None:
        """
        Writes mesh and field data to files with advanced options for binary format
        and appending field data.

        This method handles exporting mesh data and associated fields using the Gmsh
        API. Depending on the configuration, it can write data in binary or ASCII
        format, append field data to the same file, or save each field in separate files.

        Attributes:
            binary (bool): Determines whether the mesh is written in binary format.
            filename (Path): The base filename for saving the mesh and field data.
            get_append (Callable): A method that returns a boolean indicating whether
                to append field data to the same file.
            get_filename (Callable): A method that generates a new filename with a
                specified suffix.

        Behavior:
            - If `binary` is True, the mesh is written in binary format; otherwise,
              it is written in ASCII format.
            - If `get_append()` returns True, all fields are appended to the same file.
            - If `get_append()` returns False, each field is saved in a separate file
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
        gmsh.option.setNumber('PostProcessing.SaveMesh', 0)  # save mesh for each view
        if self.binary:
            gmsh.option.setNumber('Mesh.Binary', 1)
        else:
            gmsh.option.setNumber('Mesh.Binary', 0)
        # if len( gmsh.view.getTags())==0 or not self.get_append():
        gmsh.write(self.filename.as_posix())
        if self.get_append():
            for t in gmsh.view.getTags():
                viewname = get_view_name(t)
                starttime = time.perf_counter()
                gmsh.view.write(t, self.filename.as_posix(), append=True)
                txt = f'Field {viewname} save in {self.filename}'
                txt += f' ({various.convert_size(self.filename.stat().st_size)})'
                Logger.info(txt)
        else:
            it = 0
            for t in gmsh.view.getTags():
                viewname = get_view_name(t)
                viewname = viewname.replace(' ', '_')
                if len(viewname) > 15:
                    viewname = viewname[0:15]
                #
                newfilename = cast(Path, self.get_filename(suffix=f'_view-{it}_{viewname}'))
                starttime = time.perf_counter()
                gmsh.view.write(t, newfilename.as_posix(), append=False)
                txt = f'Data save in {newfilename}'
                txt += f'({various.convert_size(newfilename.stat().st_size)})'
                txt += f' - Elapsed {(time.perf_counter()-starttime):.4f} s'
                Logger.info(txt)


writer = MSHWriter  # for backward compatibility
mshWriter = MSHWriter  # legacy public API
