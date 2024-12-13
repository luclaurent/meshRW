"""
This file includes the definition and tools to manipulate files
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""
import time
from pathlib import Path

from loguru import logger as Logger

from . import various


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
        self.getFilename(Path(filename),gz,bz2)
        #open the file
        self.open(safeMode)

    def getFilename(self,filename,gz=None,bz2=None):
        """
            Load the right filename
        """
        self.compress = None
        #check extension for compression
        if filename.suffix == '.gz':
            self.compress = 'gz'
        elif filename.suffix == '.bz2':
            self.compress = 'bz2'
        elif gz:
            filename.with_suffix(filename.suffix + '.gz')
            self.compress = 'gz'
        elif bz2:
            filename.with_suffix(filename.suffix + '.bz2')
            self.compress = 'bz2'
        #extract information about filename
        self.basename = filename.name
        self.dirname = filename.absolute().parent
        self.filename = filename

    def open(self,safeMode=False):
        """
            Open the file w/- or W/o safe mode (avoid overwrite existing file
        """
        #adapt the rights (in case of the file does not exist)
        if self.append and self.filename.exists():
            Logger.warning(f'{self.basename} does not exist! Unable to append')
            self.fixRight(append = False)
        if not safeMode and self.filename.exists() and not self.append and 'w' in self.right:
            Logger.warning(f'{self.basename} already exists! It will be overwritten')
        if safeMode and self.filename.exists() and not self.append and 'w' in self.right:
            Logger.warning(f'{self.basename} already exists! Not overwrite it')
        else:
            #
            Logger.debug(f'Open {self.basename} in {self.dirname} with right {self.right}')
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
            Logger.info(f'Close file {self.basename} with elapsed time {time.perf_counter()-self.startTime:g}s - size {various.convert_size(self.filename.stat().st_size)}')

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
