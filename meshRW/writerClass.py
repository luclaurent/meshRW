from abc import ABC, abstractmethod

from datetime import datetime
from pathlib import Path
from typing import Union
import numpy as np

from loguru import logger as Logger



class writer(ABC):
    def __init__(self,
                 filename: Union[str, Path]=None,
                 nodes: Union[list, np.ndarray]=None,
                 elements: dict=None,
                 fields: Union[list, np.ndarray]=None,
                 append: bool=False,
                 title: str=None,
                 opts: dict={}):
        self.append = append        
        self.title = self.adaptTitle(txt=title)
        self.filename = Path(filename)
        self.basename = self.filename.name
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
        self.dataAnalysis(nodes,elements,fields)
        
    @abstractmethod
    def setOptions(self, opts):
        """ Set options """
        pass
    
    @abstractmethod
    def getAppend(self):
        pass 
    
    def adaptTitle(self, txt = '', append=False):
        """ Adapt title with additional information"""
        if append:
            txtFinal = self.title + txt
        else:
            txtFinal = txt
        if not txtFinal:
            txtFinal = datetime.today().strftime('%Y-%M-%d %H:%M:%s')
        return txtFinal 
    
    @abstractmethod
    def writeContents(self, nodes, elements, fields=None, numStep = None):
        """ Write contents  """
        pass
    
    def writeHeader(self):
        """ Write header to the output file """
        pass
    
    @abstractmethod
    def writeNodes(self, nodes):
        """ write nodes """
        pass
    
    @abstractmethod
    def writeElements(self, elements):
        """ write elements """
        pass
    
    @abstractmethod
    def writeFields(self, fields, numStep = None):
        """ write fields """
        pass
    
    
    def splitFilename(self):
        """
        Get the basename and extension (in list) of the filename
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
        return path,filename, extension
        
    def getFilename(self, prefix=None, suffix=None):
        """
        Add prefix and/or suffix to the filename
        """
        path, basename, extension = self.splitFilename()
        if prefix is not None:
            basename = prefix + basename
        if suffix is not None:
            basename = basename + suffix
        return path / (basename + extension)
    
    def logBadExtension(self):
        """
        """
        Logger.error('File {}: bad extension (ALLOWED: {})'.format(
            self.filename, ' '.join(self.db.ALLOWED_EXTENSIONS)))
        
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
        ## analyse fields
        if fields is not None:
            if isinstance(fields,dict):
                fields = [fields]
            self.fieldAnalysis(fields)

    def fieldAnalysis(self,fields: list):
        """ Analyse fields """
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
            if f.get('nbsteps') is not None or f.get('steps') is not None:
                self.nbTemporalFields += 1
                cSteps = []
                if f.get('steps') is not None:
                    cSteps = f.get('steps')
                cNbSteps = f.get('nbsteps',len(cSteps))
                # adapt steps 
                if len(self.steps) < cNbSteps:
                    cSteps = np.arange(cNbSteps, dtype=float)
                if cNbSteps == 0:
                    cNbSteps = len(self.steps)
                # check consistency of definition of steps
                if len(self.steps) > 0:
                    if not np.allclose(self.steps,cSteps):
                        name = f.get('name','field-{}'.format(itField))
                        Logger.error('Inconsistent steps in fields {}'.format(name))
                else:
                    self.steps = cSteps
                    self.nbSteps = cNbSteps
                    
        # show stats
        Logger.debug('Number of fields: {}'.format(self.nbFields))
        Logger.debug('Number of cell fields: {}'.format(self.nbCellFields))
        Logger.debug('Number of point fields: {}'.format(self.nbPointFields))
        Logger.debug('Number of temporal fields: {}'.format(self.nbTemporalFields))
        
        