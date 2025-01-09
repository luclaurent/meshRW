"""
This class is a part of the meshRW library and will write a msh file from a mesh using gmsh API
----
Luc Laurent - luc.laurent@lecnam.net -- 2024
"""

import time
from pathlib import Path
from typing import Union

import gmsh
import numpy as np
from loguru import logger as Logger

from . import dbmsh, various, writerClass


def getViewName(view_tag):
    return gmsh.option.getString(f'View[{gmsh.view.getIndex(view_tag)}].Name')


class mshWriter(writerClass.writer):
    def __init__(
        self,
        filename: Union[str, Path] = None,
        nodes: Union[list, np.ndarray] = None,
        elements: dict = None,
        fields: Union[list, np.ndarray] = None,
        append: bool = False,
        title: str = None,
        opts: dict = {'version': 2.2},
    ):
        #
        Logger.info('Create msh file using gmsh API')
        # adapt inputs
        nodes, elements, fields = writerClass.adaptInputs(nodes, elements, fields)
        # initialization
        super().__init__(filename, nodes, elements, fields, append, title, opts)
        # load specific configuration
        self.db = dbmsh
        #
        if self.title is None:
            self.title = 'Imported mesh'
        self.modelName = self.title

        # write contents
        self.writeContents(nodes, elements, fields)

    def getAppend(self):
        """
        Obtain the adapt flag from the handler (automatic adaptation if the file exists)
        """
        return self.append

    def setOptions(self, options: dict):
        """Default options"""
        self.version = options.get('version', 2.2)

    def writeContents(self, nodes, elements, fields):
        """Write contents"""
        # initialize gmsh
        gmsh.initialize()
        gmsh.option.setNumber('Mesh.MshFileVersion', self.version)
        gmsh.option.setNumber('PostProcessing.SaveMesh', 1)  # export mesh when save fields
        # create empty entities
        gmsh.model.add(self.modelName)
        self.entities = {}
        Logger.info(f'Create {len(self.listPhysGrp)} entities for physical group')
        for g in self.listPhysGrp:
            self.entities[g] = gmsh.model.addDiscreteEntity(3)
            gmsh.model.addPhysicalGroup(3, [self.entities[g]], g, name=self.nameGrp.get(g, None))
        # get dimension of all elements
        dimElem = set([self.db.getDim(e.get('type')) for e in elements])
        # add global physical group
        self.globEntity = dict()
        for d in dimElem:
            self.globEntity[d] = gmsh.model.addDiscreteEntity(d)
            gmsh.model.addPhysicalGroup(d, [self.globEntity[d]], self.globPhysGrp, name='Global')

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
    def writeNodes(self, nodes):
        """
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
        gmsh.model.mesh.addNodes(3, self.entities[numFgrp], nodesNum, nodes.flatten())

    @various.timeit('Elements declared')
    def writeElements(self, elements):
        """
        write elements
        input:
            elements: lists of dict of connectivity with elements type (could be reduce to only one dictionary and elements)
                    [{'connectivity':table1,'type':eltype1,'physgrp':gpr1},{connectivity':table2,'type':eltype1,'physgrp':grp2}...]
                    or
                    {'connectivity':table1,'type':eltype1,'physgrp':gpr1}

                    'connectivity': connectivity array
                    'type': type of elements (could be a string or an integer, see getGmshElemType and  gmsh documentation)
                    'physgrp' (optional): physical group (integer or array of integers to declare the physical group of each cell)
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
                    gmsh.model.mesh.addElementsByType(self.entities[p], codeElem, [], connectivity.flatten())

    @various.timeit('Fields declared')
    def writeFields(self, fields):
        """write all fields"""
        if not isinstance(fields, list):
            fields = [fields]
        Logger.info(f'Add {len(fields)} fields')
        for f in fields:
            self.writeField(f)

    def writeField(self, field):
        """write one field"""
        # load field data
        data = field.get('data')
        name = field.get('name')
        numEntities = field.get('numEntities', None)
        nbsteps = field.get('nbsteps', 1)
        steps = field.get('steps', None)
        timesteps = field.get('timesteps', None)
        dim = field.get('dim', 0)
        typeField = field.get('type')
        #
        if not name:
            name = f'{typeField}_{self.itName}'
            self.itName += 1
        if not steps and nbsteps:
            steps = np.arange(nbsteps, dtype=int)
        if not timesteps:
            timesteps = np.zeros(nbsteps)
        if nbsteps == 1 and len(data) > 1:
            data = [data]

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
            gmsh.view.addModelData(tagView, s, self.modelName, nameTypeData, numEntities, dataView)
            # ,
            # numComponents=dim,
            # partition=0)

    @various.timeit('File(s) written')
    def writeFiles(self):
        """Advanced writing to export mesh and fields"""
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
