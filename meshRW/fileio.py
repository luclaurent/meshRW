"""
This file includes the definition and tools to manipulate files
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""
import os
import logging
import time
from . import customLogging
from . import various

# load Logger
Logger = logging.getLogger(__name__)
# if not Logger.hasHandlers():
#     LogObj = customLogging.customLogger(loggerRoot=Logger, activate=True)
#     Logger = LogObj.getLogger()

class fileHandler:

    def __init__(self,
                filename=None,
                append=None,
                right='w',
                gz=False,
                bz2=False,
                safeMode=False):
        """ 
        create the class 
        arguments:
            - filename: name of the file to open
            - append: append to existing file (override 'right')
            - right: specific right when open the file ('r','a','w'...)
            - gz: on the fly compress file with gunzip
            - bz2: on the fly compress file with bunzip2
            - safeMode: avoid overwritten
        """
        self.filename = None
        self.dirname = None
        self.fhandle = None
        self.right = right
        self.append = None
        self.compress = None
        self.startTime = 0
        #
        self.fixRight(append = append,right = right)

        #check arguments
        checkOk=True
        if not filename:
            checkOk = False
            Logger.error('Filename argument missing')
        if not right and not append:
            checkOk = False
            Logger.error('Right(s) not provided')
        #load the filename
        self.getFilename(filename,gz,bz2)
        #open the file
        self.open(safeMode)

    def getFilename(self,filename,gz=None,bz2=None):
        """
            Load the right filename
        """
        self.compress = None
        #check extension for compression
        if os.path.splitext(filename) == '.gz':
            self.compress = 'gz'
        elif os.path.splitext(filename) == '.bz2':           
            self.compress = 'bz2'
        else:
            if gz:
                filename += '.gz'
                self.compress = 'gz'
            elif bz2:
                filename += '.bz2'
                self.compress = 'bz2'
        #extract information about filename
        self.basename = os.path.basename(filename)
        self.dirname = os.path.dirname(filename)
        if not self.dirname:
            self.dirname = os.getcwd()
        self.filename = filename

    def open(self,safeMode=False):
        """
            Open the file w/- or W/o safe mode (avoid overwrite existing file
        """
        #adapt the rights (in case of the file does not exist)
        if self.append and os.path.exists(self.filename):
            Logger.warning('{} does not exist! Unable to append'.format(self.basename))
            self.fixRight(append = False)
        if not safeMode and os.path.exists(self.filename) and not self.append and 'w' in self.right:
            Logger.warning('{} already exists! It will be overwritten'.format(self.basename))
        if safeMode and os.path.exists(self.filename) and not self.append and 'w' in self.right:
            Logger.warning('{} already exists! Not overwrite it'.format(self.basename))
        else:
            #
            Logger.debug('Open {} in {} with right {}'.format(self.basename,self.dirname,self.right))
            # open file
            if self.compress == 'gz':
                Logger.debug('Use GZ lib')
                import gzip
                self.fhandle = gzip.open(self.filename, self.right)
            elif self.compress == 'bz2':
                Logger.debug('Use BZ2 lib')
                import bz2
                self.fhandle = bz2.open(self.filename, self.right)
            else:
                self.fhandle = open(self.filename, self.right)
        #store timestamp at opening
        self.startTime = time.perf_counter()
        return self.fhandle
    
    def close(self):
        """
        Close openned file
        """
        if self.fhandle:
            self.fhandle.close()
            self.fhandle = None
            Logger.info('Close file {} with elapsed time {:g}s - size {}'.format(
                self.basename,
                time.perf_counter()-self.startTime,
                various.convert_size(os.path.getsize(self.filename))))
    
    def getHandler(self):
        """
        get the file handler
        """
        return self.fhandle
    
    def write(self,txt):
        """
        write in the file using handle
        """
        return self.fhandle.write(txt)
    
    def fixRight(self,append = None, right = None):
        """
        Fix issue on right to write file
        """
        if append is not None:
            self.append = append
            if append:
                self.right = 'a'
            else:
                self.right = 'w'
        else:
            self.right=right
            if right[0] == 'w':
                self.append = False
            elif right[0] == 'a':
                self.append = True