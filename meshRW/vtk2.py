"""
This file is part of the meshRW package
---
This class is a part of the meshRW library and will write a vtk file from a mesh using libvtk
----
Luc Laurent - luc.laurent@lecnam.net -- 2024
"""

from pathlib import Path
from typing import Union, Optional
import sys

import time

import numpy as np
import vtk
import vtkmodules.util.numpy_support as ns
from loguru import logger as Logger
from lxml import etree

from . import configMESH, dbvtk, various, writerClass


class vtkWriter(writerClass.writer):
    """
    vtkWriter is a class for writing VTK/VTU files using the VTK library. It provides functionality to handle nodes, elements, 
    and fields, and supports writing data along multiple time steps. The class also includes methods for creating new fields 
    from physical groups, setting field data, and writing PVD files for time-dependent datasets.
    Attributes:
        ugrid (vtk.vtkUnstructuredGrid): The unstructured grid object for VTK data.
        writer (vtk.vtkXMLUnstructuredGridWriter): The writer object for saving VTK files.
        db (module): The database module for VTK-specific configurations.
    Methods:
        __init__(filename, nodes, elements, fields, append, title, verbose, opts):
            Initializes the vtkWriter object with the given parameters and prepares the data for writing.
        getAppend():
            Returns the append option.
        setOptions(options):
            Sets the default options for writing files (binary or ASCII).
        writeContentsSteps(nodes, elements, fields):
            Writes the content along multiple time steps, if applicable.
        writePVD(dataPVD):
            Writes a PVD file for time-dependent datasets.
        writeContents(fields, numStep):
            Adds fields to the VTK data, depending on the version and time step.
        writeFields(fields, numStep):
            Writes the fields (nodal or elemental) to the VTK data.
        writeNodes(nodes):
            Adds nodes to the VTK unstructured grid.
        writeElements(elements):
            Adds elements to the VTK unstructured grid.
        createNewFields(elems):
            Creates new fields from element data, such as physical groups.
        setField(field, numStep):
            Sets the field data and initializes the corresponding VTK array.
        write(ugrid, filename):
            Writes the VTK unstructured grid to a file.
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
        opts: dict = {'binary': False, 'ascii': True},
    )-> None:
        """
        Initialize the VTK writer class.

        Parameters:
            filename (Union[str, Path], optional): The file path for the VTK file. Defaults to None.
            nodes (Union[list, np.ndarray], optional): The list or array of nodes. Defaults to None.
            elements (dict, optional): The dictionary of elements. Defaults to None.
            fields (Union[list, np.ndarray], optional): The list or array of fields. Defaults to None.
            append (bool, optional): Whether to append to an existing file. Defaults to False.
            title (str, optional): The title of the VTK file. Defaults to None.
            verbose (bool, optional): Whether to enable verbose logging. Defaults to False.
            opts (dict, optional): Options for file writing, such as binary or ASCII mode. 
                Defaults to {'binary': False, 'ascii': True}.

        Notes:
            - This method initializes the VTK writer, adapts inputs, prepares new fields, 
              and writes the contents depending on the number of steps.
            - The `Logger` is used for logging, and verbosity can be adjusted.
            - The `dbvtk` configuration is loaded for specific settings.
        """
        # # adapt verbosity logger
        # if not verbose:
        #     Logger.remove()
        #     Logger.add(sys.stderr, level="INFO") 
        #
        Logger.info('Start writing vtk/vtu file using libvtk')
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
        # vtk data
        self.ugrid = None
        self.writer = None
        # load specific configuration
        self.db = dbvtk
        # write contents depending on the number of steps
        self.writeContentsSteps(nodes, elements, fields)

    def getAppend(self)-> bool:
        """"
        Retrieves the current state of the append option.

        Returns:
            bool: The value of the append option, indicating whether appending is enabled.
        """
        return self.append

    def setOptions(self, options: dict)-> None:
        """
        Sets the options for the object.

        Args:
            options (dict): A dictionary containing configuration options. 
                Supported keys:
                    - 'binary' (bool): If True, enables binary mode. Defaults to False.
                    - 'ascii' (bool): If True, enables ASCII mode. Defaults to False.

        Returns:
            None
        """
        self.binary = options.get('binary', False)
        self.ascii = options.get('ascii', False)

    def writeContentsSteps(self, 
                           nodes: Union[list, np.ndarray], 
                           elements: Union[list, np.ndarray, dict], 
                           fields: Optional[Union[list, np.ndarray]] = None)-> None:
        """
        Write content to files along multiple steps or as a single output.

        This method handles the process of writing nodes, elements, and optional fields
        to VTK files. It supports writing data for multiple time steps and generates
        corresponding PVD files for visualization.

        Args:
            nodes (Union[list, np.ndarray]): The list or array of node coordinates.
            elements (Union[list, np.ndarray, dict]): The list, array, or dictionary of elements.
            fields (Optional[Union[list, np.ndarray]]): Optional list or array of field data
                to be written. Defaults to None.

        Returns:
            None

        Behavior:
            - If `self.nbSteps` > 0:
                - Writes data for each time step, generating separate files for each step.
                - Updates a dictionary (`dataPVD`) to map time steps to filenames.
                - Writes a PVD file for time step visualization.
            - If `self.nbSteps` == 0:
                - Writes a single file with the provided data.

        Notes:
            - The method uses helper functions such as `writeNodes`, `writeElements`,
              `writeContents`, `getFilename`, and `writePVD` to perform specific tasks.
            - The filenames for time steps are suffixed with the step number, zero-padded
              to match the number of steps.
        """
        # create dictionary for preparing pvd file writing
        if self.nbSteps > 0:
            dataPVD = dict()
        # initialize data
        # create UnstructuredGrid
        self.ugrid = vtk.vtkUnstructuredGrid()
        # add points
        self.writeNodes(nodes)
        # elements
        self.writeElements(elements)
        # write along steps
        if self.nbSteps > 0:
            for itS in range(self.nbSteps):
                # add fieds
                self.writeContents(fields, numStep=itS)
                # adapt the filename
                filename = self.getFilename(suffix='.' + str(itS).zfill(len(str(self.nbSteps))))
                # write file
                self.write(self.ugrid, filename)
                # update PVD dict
                dataPVD[self.steps[itS]] = filename.name

                # # adapt title
                # self.title = self.adaptTitle(txt=f' step num {itS:d}', append=True)
            # write pvd file
            self.writePVD(dataPVD)
        else:
            # add fieds
            self.writeContents(fields)
            # write file
            filename = self.getFilename()
            self.write(self.ugrid, filename)

    def writePVD(self, dataPVD: dict)-> None:
        """
        Write a PVD (ParaView Data) file.

        This method generates a PVD file, which is an XML-based format used by ParaView
        to describe a collection of datasets over time. The method takes a dictionary
        where the keys represent timesteps and the values are the corresponding file paths
        for the datasets.

        Args:
            dataPVD (dict): A dictionary where keys are timesteps (int or float) and values
                            are file paths (str) to the datasets.

        Returns:
            None

        Raises:
            OSError: If there is an issue writing the PVD file to disk.

        Notes:
            - The generated PVD file includes a root element `<VTKFile>` with a child
              `<Collection>` element containing `<DataSet>` elements for each timestep.
            - The method logs the file size and elapsed time for writing the PVD file.
        """
        filename = self.getFilename(extension='.pvd')
        # create root element
        root = etree.Element('VTKFile', type='Collection', version='0.1')

        # Create collection elements
        collection = etree.SubElement(root, 'Collection')

        # Loop on timesteps and files for dataset
        for timestep, file in dataPVD.items():
            dataset = etree.Element('DataSet', timestep=str(timestep), part='0', file=file)
            collection.append(dataset)

        # convert xml tree to string
        xml_str = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')

        # write in file
        starttime = time.perf_counter()
        with open(filename, 'wb') as f:
            f.write(xml_str)
        Logger.info(
                f'PVD file written {filename} ({various.convert_size(filename.stat().st_size)}) - Elapsed {(time.perf_counter()-starttime):.4f} s'
            )


    @various.timeit('Fields declared')
    def writeContents(self, 
                      fields: Optional[Union[list, np.ndarray]] = None, 
                      numStep: Optional[int] = None)-> None:
        """
        Writes the contents of the fields to the appropriate output format.

        This method handles the addition of fields to the output, depending on the 
        version or format being used. It delegates the actual writing of fields 
        to the `writeFields` method.

        Args:
            fields (Optional[Union[list, np.ndarray]]): The fields to be written. 
            This can be a list or a NumPy array. Defaults to None.
            numStep (Optional[int]): The step number associated with the fields. 
            This is used to track the time step or iteration. Defaults to None.

        Returns:
            None
        """
        self.writeFields(fields, numStep=numStep)

    def writeFields(self,                     
                    fields: Optional[Union[list, np.ndarray]] = None, 
                    numStep: Optional[int]=None)-> None:
        """
        Write fields to the unstructured grid (ugrid) object.

        This method adds the provided fields to the appropriate data container
        (point data or cell data) of the unstructured grid based on the field type.

        Args:
            fields (Optional[Union[list, np.ndarray]]): A list or a single numpy array 
                representing the fields to be added. If a single field is provided, 
                it will be converted into a list.
            numStep (Optional[int]): An optional integer representing the time step 
                or iteration number associated with the fields.

        Returns:
            None

        Raises:
            ValueError: If the field type is not recognized.

        Notes:
            - The method uses the `setField` function to process each field and 
                determine its type ('nodal' or 'elemental').
            - 'nodal' fields are added to the point data of the unstructured grid.
            - 'elemental' fields are added to the cell data of the unstructured grid.
            - If the field type is not recognized, an error is logged.
        """
        if fields is not None:
            if not isinstance(fields, list):
                fields = [fields]
            Logger.info(f'Add {len(fields)} fields')
            for f in fields:
                data, typedata = self.setField(f, numStep=numStep)
                if typedata == 'nodal':
                    self.ugrid.GetPointData().AddArray(data)
                elif typedata == 'elemental':
                    self.ugrid.GetCellData().AddArray(data)
                else:
                    Logger.error(f'Field type {typedata} not recognized')

    @various.timeit('Nodes declared')
    def writeNodes(self, nodes: Union[list, np.ndarray])-> None:
        """
        Writes the given nodes to the VTK unstructured grid.

        This method takes a list or numpy array of nodes and adds them as points
        to the VTK unstructured grid (`ugrid`). Each node is expected to be a 
        3D coordinate.

        Args:
            nodes (Union[list, np.ndarray]): A list or numpy array of shape (N, 3),
            where N is the number of nodes, and each node is represented by 
            its 3D coordinates (x, y, z).

        Returns:
            None
        """
        points = vtk.vtkPoints()
        for i in range(len(nodes)):
            points.InsertNextPoint(nodes[i, :])
        self.ugrid.SetPoints(points)

    @various.timeit('Elements declared')
    def writeElements(self, elements: Union[list, np.ndarray, dict])-> None:
        """
        Writes elements to the unstructured grid (ugrid) based on the provided input.

        Args:
            elements (Union[list, np.ndarray, dict]): A collection of elements to be added. 
                Each element is expected to be a dictionary containing:
                    - 'type' (str): The type of the element (e.g., VTK cell type).
                    - 'connectivity' (list or array): The connectivity data defining the element.
                    - 'physgrp' (optional): Physical group identifier for the element.

        Raises:
            KeyError: If required keys ('type' or 'connectivity') are missing in an element.

        Notes:
            - The method uses the `dbvtk.getVTKObj` function to retrieve the VTK cell object 
              and the number of nodes for the given element type.
            - Each element's connectivity is used to set the point IDs for the VTK cell, 
              which is then inserted into the unstructured grid.
            - Debug logs are generated to indicate the number and type of elements being processed.

        """
        for m in elements:
            # get connectivity data
            typeElem = m.get('type')
            connectivity = m.get('connectivity')
            physgrp = m.get('physgrp', None)
            # load element's vtk class
            cell, nbnodes = dbvtk.getVTKObj(typeElem)
            Logger.debug(f'Set {len(connectivity)} elements of type {typeElem}')
            #
            for t in connectivity:
                for i in range(nbnodes):
                    cell.GetPointIds().SetId(i, t[i])
                self.ugrid.InsertNextCell(cell.GetCellType(), cell.GetPointIds())

    def createNewFields(self, 
                        elems: Union[list, np.ndarray, dict])-> Optional[list]:
        """
        Create new fields based on the provided elements data.

        This method processes the input `elems` to prepare new fields, particularly
        for physical groups if they exist in the data. It checks for the presence
        of a physical group key in the elements and constructs a new field accordingly.

        Args:
            elems (Union[list, np.ndarray, dict]): A collection of elements data. Each
                element is expected to be a dictionary containing mesh and optionally
                physical group information.

        Returns:
            Optional[list]: A list of dictionaries representing the new fields if a
            physical group is found. Each dictionary contains:
                - 'data': A NumPy array of physical group data for the elements.
                - 'type': The type of the field, which is 'elemental'.
                - 'dim': The dimensionality of the field, which is 1.
                - 'name': The name of the field, corresponding to the physical group key.
            Returns None if no physical group is found in the input elements.

        Notes:
            - The method assumes that the physical group data, if present, is either
              a single value or an array matching the number of elements in the mesh.
            - If no physical group data is found, the method assigns a default value
              of -1 to the field data.
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
            newFields.extend([{'data': data, 'type': 'elemental', 'dim': 1, 'name': configMESH.DFLT_PHYS_GRP}])

        return newFields
    
    def setField(self, 
                 field: dict, 
                 numStep: Optional[int]=None)-> tuple:
        """
        Sets a field in the VTK format from the provided field data.

        Args:
            field (dict): A dictionary containing field data with the following keys:
                - 'data': The field data as a numpy array.
                - 'name': The name of the field (string).
                - 'numEntities' (optional): The number of entities in the field (int).
                - 'nbsteps' (optional): The number of time steps (int, default is 1).
                - 'steps' (optional): The indices of the time steps (array-like).
                - 'dim' (optional): The dimensionality of the field (int, default is 0).
                - 'timesteps' (optional): The time values corresponding to the steps (array-like).
                - 'type': The type of the field (string).
            numStep (Optional[int]): The specific time step to extract if the field is time-dependent.

        Returns:
            tuple: A tuple containing:
                - dataVtk: The VTK-compatible array created from the field data.
                - typeField: The type of the field as provided in the input dictionary.

        Notes:
            - If the field is time-dependent and `numStep` is provided, the function extracts
              the data corresponding to the specified time step.
            - The function initializes a VTK array using the provided field data and sets its name.
        """
        # load field data
        data = field.get('data')
        name = field.get('name')
        numEntities = field.get('numEntities', None)
        nbsteps = field.get('nbsteps', 1)
        steps = field.get('steps', None)
        dim = field.get('dim', 0)
        timesteps = field.get('timesteps', None)
        typeField = field.get('type')
        # for time dependent data
        if numStep is not None:
            # manage steps
            if steps is not None:
                nbsteps = len(steps)
            if timesteps is not None:
                nbsteps = len(timesteps)
            if nbsteps is None:
                nbsteps = 1
            #
            if not steps and nbsteps>1:
                steps = np.arange(nbsteps, dtype=int)
            if not timesteps and nbsteps>1:
                timesteps = np.zeros(nbsteps)

            if nbsteps > 1 or steps is not None:
                data = data[numStep]
        # initialize VTK's array
        dataVtk = ns.numpy_to_vtk(data)
        # dataVtk = vtk.vtkDoubleArray()
        dataVtk.SetName(name)
        # if len(data.shape) == 1:
        #     dim = 1
        # else:
        #     dim = data.shape[1]
        # for _,c in enumerate(data):
        #     if dim == 1:
        #         dataVtk.InsertNextValue(c)
        #     elif dim == 2:
        #         dataVtk.InsertNextTuple2(*c)
        #     elif dim == 3:
        #         dataVtk.InsertNextTuple3(*c)
        #     elif dim == 4:
        #         dataVtk.InsertNextTuple4(*c)
        #     elif dim == 6:
        #         dataVtk.InsertNextTuple6(*c)
        #     elif dim == 9:
        #         dataVtk.InsertNextTuple9(*c)
        # #
        return dataVtk, typeField

    def write(self, 
              ugrid: Optional[vtk.vtkUnstructuredGrid]=None, 
              filename: Optional[str]=None)-> None:
        """
        Writes a VTK unstructured grid to a file.
        This method writes the provided VTK unstructured grid (`ugrid`) to a file
        specified by `filename`. It supports both binary and ASCII formats, depending
        on the configuration of the writer. If no `ugrid` is provided, the instance's
        `ugrid` attribute is used.
        Args:
            ugrid (Optional[vtk.vtkUnstructuredGrid]): The unstructured grid to write.
            If None, the instance's `ugrid` attribute is used.
            filename (Optional[str]): The name of the file to write to. If None, the
            method will not proceed with writing.
        Returns:
            None
        Raises:
            ValueError: If `filename` is not provided or is invalid.
        Notes:
            - The method initializes the writer if it has not been set up already.
            - The file format (binary or ASCII) is determined by the `binary` and
              `ascii` attributes of the instance.
            - Logs the size of the saved file and the time taken to write it.
        """
        # initialization
        if self.writer is None:
            self.writer = vtk.vtkXMLUnstructuredGridWriter()
            self.writer.SetInputDataObject(self.ugrid)
            if self.binary:
                self.writer.SetFileType(vtk.VTK_BINARY)
            if self.ascii:
                self.writer.SetDataModeToAscii()
        self.writer.SetFileName(filename)
        self.writer.Update()
        # self.writer.SetDebug(True)
        # self.writer.SetWriteTimeValue(True)
        
        starttime = time.perf_counter()
        self.writer.Write()
        Logger.info(f'Data save in {filename} ({various.convert_size(filename.stat().st_size)}) - Elapsed {(time.perf_counter()-starttime):.4f} s')
