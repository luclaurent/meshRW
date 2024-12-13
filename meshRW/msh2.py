"""
This class is a part of the meshRW library and will write a msh file from a mesh using gmsh API
----
Luc Laurent - luc.laurent@lecnam.net -- 2024
"""

import gmsh
from . import dbmsh
import numpy as np
from loguru import logger as Logger

class mshWriter():
    
    def __init__(self,nodes,elems,
                    fields=None,
                    filename=None,
                    version=2.2):
        # 
        self.modelName = "Imported mesh"
        self.itName = 0
        
        # initialize gmsh
        gmsh.initialize()
        gmsh.option.setNumber("Mesh.MshFileVersion",2.2) 
        # create empty entity
        gmsh.model.add(self.modelName)
        vol = gmsh.model.addDiscreteEntity(3)
 
        # add nodes
        self.nbNodes = len(nodes)
        nodesNum = np.arange(1,len(nodes)+1)
        gmsh.model.mesh.addNodes(3,vol,nodesNum,nodes.flatten())
        
        # add elements
        self.nbElems = 0
        for m in elems:
            typeElem = m.get('type')
            connectivity = m.get('connectivity')
            physgrp = m.get('physgrp',None)
            codeElem = dbmsh.getMSHElemType(typeElem)
            #
            self.nbElems += len(connectivity)
            #
            gmsh.model.mesh.addElementsByType(vol,codeElem,[],connectivity.flatten())
            if physgrp is not None:
                if not isinstance(physgrp,np.ndarray) or not isinstance(physgrp,list):
                    physgrp = [physgrp]
                for p in np.unique(physgrp):
                    gmsh.model.addPhysicalGroup(3,[vol],p)
        
        gmsh.model.mesh.reclassifyNodes()
        
        # add fields
        if not isinstance(fields, list):
            fields = [fields]
        for f in fields:
            self.setField(f)
        
        # write msh file
        gmsh.write(str(filename))
        
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
            name = '{}_{}'.format(typeField,self.itName)
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
            gmsh.view.addModelData(tagView,
                                    s,
                                    self.modelName,
                                    nameTypeData,
                                    numEntities,
                                    data[s],
                                    time=t,
                                    numComponents=dim,
                                    partition=0)
        
        pass
        