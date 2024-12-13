"""
This class is a part of the meshRW library and will write a msh file from a mesh using gmsh API
----
Luc Laurent - luc.laurent@lecnam.net -- 2024
"""
import time
import gmsh
import numpy as np
from loguru import logger as Logger
from pathlib import Path

from . import dbmsh
from . import various

def getViewName(view_tag):
        return gmsh.option.getString(f'View[{gmsh.view.getIndex(view_tag)}].Name')
                
class mshWriter:

    def __init__(self,
                 nodes,
                 elems,
                 fields=None,
                 filename=None,
                 version=2.2,
                 append=False):
        #
        Logger.info('Create msh file using gmsh API')
        self.modelName = "Imported mesh"
        self.itName = 0
        self.append = append # add all fields to the exported mesh file
        self.filename = Path(filename)
        
        # initial data analysis
        self.dataAnalysis(nodes,elems,fields)

        # initialize gmsh
        gmsh.initialize()
        gmsh.option.setNumber("Mesh.MshFileVersion",version)
        gmsh.option.setNumber("PostProcessing.SaveMesh",1)  # export mesh when save fields
        # create empty entities
        gmsh.model.add(self.modelName)
        self.entities = {}
        Logger.info('Create {} entities for physical group'.format(len(self.listPhysGrp)))
        for g in self.listPhysGrp:
            self.entities[g] = gmsh.model.addDiscreteEntity(3)
            gmsh.model.addPhysicalGroup(3,
                                        [self.entities[g]],
                                        g,
                                        name = self.nameGrp.get(g,None))
        # add global physical group
        self.globEntity = gmsh.model.addDiscreteEntity(3)
        gmsh.model.addPhysicalGroup(3,
                                    [self.globEntity],
                                    self.globPhysGrp,
                                    name = 'Global')

        # add nodes
        Logger.info('Add {} nodes'.format(self.nbNodes))
        nodesNum = np.arange(1,len(nodes)+1)
        numFgrp = self.listPhysGrp[0]
        # add nodes to first volume entity
        gmsh.model.mesh.addNodes(3,
                                 self.entities[numFgrp],
                                 nodesNum,
                                 nodes.flatten())

        # add elements
        Logger.info('Add {} elements'.format(self.nbElems))
        for m in elems:
            # get connectivity data
            typeElem = m.get('type')
            connectivity = m.get('connectivity')
            physgrp = m.get('physgrp',None)
            codeElem = dbmsh.getMSHElemType(typeElem)
            #
            Logger.info('Set {} elements of type {}'.format(len(connectivity),typeElem))
            gmsh.model.mesh.addElementsByType(self.globEntity,
                                              codeElem,
                                              [],
                                              connectivity.flatten())
            if physgrp is not None:
                if not isinstance(physgrp,np.ndarray) and not isinstance(physgrp,list):
                    physgrp = [physgrp]
                for p in physgrp:
                    gmsh.model.mesh.addElementsByType(self.entities[p],
                                                      codeElem,
                                                      [],
                                                      connectivity.flatten())
                
        # add fields
        if not isinstance(fields, list):
            fields = [fields]
        for f in fields:
            self.setField(f)
        
        gmsh.model.mesh.reclassifyNodes()

        # write msh file
        self.write()
        # clean gmsh
        gmsh.finalize()
        
        
    def write(self):
        """ Advanced writing to export mesh and fields """
        gmsh.write(self.filename.as_posix())
        if self.append:
            for t in gmsh.view.getTags():
                starttime = time.perf_counter()
                gmsh.view.write(t,self.filename.as_posix(),append=True)
                Logger.info('Data save in {} ({}) - Elapsed {}s'.format(self.filename,
                                                     various.convert_size(self.filename.stat().st_size),
                                                     time.perf_counter()-starttime))
        else:
            it = 0
            for t in gmsh.view.getTags():
                viewname = getViewName(t)
                viewname=viewname.replace(' ','_')
                if len(viewname)>15:
                    viewname = viewname[0:15]
                #
                newfilename = self.getFilename(suffix='_view-{}_{}'.format(it,viewname))
                starttime = time.perf_counter()
                gmsh.view.write(t,newfilename.as_posix(),append=False)
                Logger.info('Data save in {} ({}) - Elapsed {}s'.format(newfilename,
                                                     various.convert_size(newfilename.stat().st_size),
                                                     time.perf_counter()-starttime))
    
    
    def getFilename(self, prefix=None, suffix=None):
        """
        Add prefix and/or suffix to the filename
        """
        path = self.filename.parent
        basename = self.filename.stem
        extension = self.filename.suffix
        if prefix is not None:
            basename = prefix + basename
        if suffix is not None:
            basename = basename + suffix
        return path / (basename + extension) 
     
        
        
    def dataAnalysis(self,nodes,elems,fields):
        """ """
        self.nbNodes = len(nodes)    
        self.nbElems = 0    
        #
        self.elemPerType = {}
        self.elemPerGrp = {}
        self.nameGrp = {}
        #
        if isinstance(elems,dict):
            elems = [elems]
        #
        itGrpE = 0
        for e in elems:
            if e.get('type') not in self.elemPerType:
                self.elemPerType[e.get('type')] = 0
            self.elemPerType[e.get('type')] += len(e.get('connectivity'))
            self.nbElems += len(e.get('connectivity'))
            name = e.get('name','grp-{}'.format(itGrpE))
            itGrpE += 1
            if e.get('physgrp') is not None:
                if not isinstance(e.get('physgrp'),list) or not isinstance(e.get('physgrp'),list):
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
        numinit = 1000
        numit = 50
        current = numinit
        while current in self.listPhysGrp:
            current += numit
        self.globPhysGrp = current
        # show stats
        Logger.debug('Number of nodes: {}'.format(self.nbNodes))
        Logger.debug('Number of elements: {}'.format(self.nbElems))
        Logger.debug('Number of physical groups: {}'.format(len(self.listPhysGrp)))
        for t,e in self.elemPerType.items():
            Logger.debug('Number of {} elements: {}'.format(t,e))
        for g in self.listPhysGrp:
            Logger.debug('Number of elements in group {}: {}'.format(g,self.elemPerGrp.get(g,0)))
        Logger.debug('Global physical group: {}'.format(self.globPhysGrp))
        # create artificial physical group if necessary
        if len(self.listPhysGrp) == 0:
            self.listPhysGrp = [1]
        

    def setField(self,field):
        """ """
        # load field data
        data = field.get('data')
        name = field.get('name')
        numEntities = field.get('numEntities',None)
        nbsteps = field.get('nbsteps',1)
        steps = field.get('steps',None)
        timesteps = field.get('timesteps',None)
        dim = field.get('dim',0)
        typeField = field.get('type')
        #
        if not name:
            name = f'{typeField}_{self.itName}'
            self.itName += 1
        if not steps and nbsteps:
            steps = np.arange(nbsteps, dtype=int)
        if not timesteps:
            timesteps = np.zeros(nbsteps)
        if nbsteps ==1 and len(data) > 1:
            data = [data]

        # add field
        if typeField == 'nodal':
            nameTypeData = 'NodeData'
            if numEntities is None:
                numEntities = np.arange(1,self.nbNodes+1)

        elif typeField == 'elemental':
            nameTypeData = 'ElementData'
            if numEntities is None:
                numEntities = np.arange(1,self.nbElems+1)
        else:
            raise ValueError('typeField must be nodal or elemental')
        #
        tagView = gmsh.view.add(name)
        for s,t in zip(steps,timesteps):
            dataView = data[s]
            if len(dataView.shape) == 1:
                dataView = dataView.reshape((-1,1))
            gmsh.view.addModelData(tagView,
                                    s,
                                    self.modelName,
                                    nameTypeData,
                                    numEntities,
                                    dataView)
                                    #,
                                    # numComponents=dim,
                                    # partition=0)


