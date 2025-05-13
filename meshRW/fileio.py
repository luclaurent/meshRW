"""
This file is part of the meshRW package
---
This file includes the definition and tools to manipulate files
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""
from typing import Union, Optional
import time
from pathlib import Path

from loguru import logger as Logger

from . import various


class fileHandler:
    """
    fileHandler is a class designed to handle file operations with support for 
    compression, safe mode, and flexible file access rights. It provides methods 
    to open, write, and close files while ensuring proper error handling and logging.

        right (str): The mode used to open the file ('r', 'w', 'a', etc.).

    Methods:
        __init__(filename: Union[str, Path]=None, append: Optional[bool]=None, 
                 right: str='w', gz: bool=False, bz2: bool=False, 
                 safeMode: bool=False) -> None:
            Initializes the fileHandler class with the specified parameters.

        getFilename(filename: Path, gz: bool=False, bz2: bool=False) -> None:
            Determines the appropriate filename and compression type based on the 
            provided file path and optional compression flags.

        open(safeMode: bool=False) -> object:

        close() -> None:
            Closes the currently opened file and logs information about the file.

        getHandler() -> object:

        write(txt: Union[str, bytes]) -> int:

        fixRight(append: Optional[bool]=None, right: Optional[str]=None) -> None:
            Adjusts the file writing mode and append behavior based on the provided 
            arguments.

        ValueError: If 'filename' is not provided or if neither 'right' nor 'append' 
                    is specified during initialization.
        FileExistsError: If safe mode is enabled and the file already exists.
        TypeError: If invalid types are provided for certain arguments.
        AttributeError: If attempting to close a file without a valid file handle.
    """
    
    def __init__(self,                 
                filename: Union[str, Path]=None, 
                append: Optional[bool]=None, 
                right: str='w', 
                gz: bool=False, 
                bz2: bool=False, 
                safeMode: bool=False)-> None:
        """
        Initializes the file handling class.

        Args:
            filename (Union[str, Path], optional): Name of the file to open. Defaults to None.
            append (Optional[bool], optional): If True, appends to an existing file (overrides 'right'). Defaults to None.
            right (str, optional): Specifies the mode to open the file ('r', 'a', 'w', etc.). Defaults to 'w'.
            gz (bool, optional): If True, enables on-the-fly compression with gzip. Defaults to False.
            bz2 (bool, optional): If True, enables on-the-fly compression with bzip2. Defaults to False.
            safeMode (bool, optional): If True, prevents overwriting of existing files. Defaults to False.

        Attributes:
            filename (Optional[Path]): The resolved file path.
            dirname (Optional[Path]): The directory of the file.
            fhandle (Optional[IO]): The file handle for the opened file.
            right (str): The mode used to open the file.
            append (Optional[bool]): Indicates if the file is opened in append mode.
            compress (Optional[str]): The compression method used ('gz', 'bz2', or None).
            startTime (float): The timestamp when the file operation starts.

        Raises:
            ValueError: If 'filename' is not provided or if neither 'right' nor 'append' is specified.
        """
        self.filename = None
        self.dirname = None
        self.fhandle = None
        self.right = right
        self.append = None
        self.compress = None
        self.startTime = 0
        #
        self.fixRight(append=append, right=right)

        # check arguments
        checkOk = True
        if not filename:
            checkOk = False
            Logger.error('Filename argument missing')
        if not right and not append:
            checkOk = False
            Logger.error('Right(s) not provided')
        # load the filename
        self.getFilename(Path(filename), gz, bz2)
        # open the file
        self.open(safeMode)

    def getFilename(self, filename: Path, gz: bool=False, bz2: bool=False)-> None:
        """
        Determines the appropriate filename and compression type based on the provided
        file path and optional compression flags.

        Args:
            filename (Path): The input file path.
            gz (bool, optional): If True, appends a '.gz' extension to the filename 
                if no compression is detected. Defaults to False.
            bz2 (bool, optional): If True, appends a '.bz2' extension to the filename 
                if no compression is detected. Defaults to False.

        Attributes Set:
            self.compress (str or None): The compression type ('gz', 'bz2', or None).
            self.basename (str): The name of the file (including extension).
            self.dirname (Path): The absolute parent directory of the file.
            self.filename (Path): The full file path.

        Notes:
            - If the file already has a '.gz' or '.bz2' extension, the corresponding 
              compression type is set, and the filename remains unchanged.
            - If no compression is detected and `gz` or `bz2` is True, the respective 
              extension is appended to the filename, and the compression type is set.
        """
        self.compress = None
        # check extension for compression
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
        # extract information about filename
        self.basename = filename.name
        self.dirname = filename.absolute().parent
        self.filename = filename

    def open(self, safeMode: bool=False)-> object:
        """
        Opens a file with specified access rights and optional safe mode.

        Parameters:
            safeMode (bool): If True, prevents overwriting an existing file. 
                             Defaults to False.

        Returns:
            object: A file handle to the opened file.

        Behavior:
            - If `append` mode is enabled and the file does not exist, logs a warning 
              and adjusts the access rights to disable append mode.
            - If `safeMode` is True and the file exists, prevents overwriting and logs a warning.
            - If `safeMode` is False and the file exists, allows overwriting and logs a warning.
            - Supports opening files with optional compression (`gz` or `bz2`).
            - Logs debug information about the file opening process.
            - Records the timestamp when the file is opened.
        """
        # adapt the rights (in case of the file does not exist)
        if self.append and not self.filename.exists():
            Logger.warning(f'{self.basename} does not exist! Unable to append')
            self.fixRight(append=False)
        if not safeMode and self.filename.exists() and not self.append and 'w' in self.right:
            Logger.warning(f'{self.basename} already exists! It will be overwritten')
        if safeMode and self.filename.exists() and not self.append and 'w' in self.right:
            Logger.error(f'{self.basename} already exists! Not overwrite it')
            raise(FileExistsError)
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
        # store timestamp at opening
        self.startTime = time.perf_counter()
        return self.fhandle

    def close(self)-> None:
        """
        Closes the currently opened file.

        This method ensures that the file handle is properly closed and set to None.
        It also logs information about the file, including its name, the elapsed time
        since it was opened, and its size.

        Raises:
            AttributeError: If `self.fhandle` is not defined or is not a valid file handle.
        """
        if self.fhandle:
            self.fhandle.close()
            self.fhandle = None
            Logger.info(
                f'Close file {self.basename} with elapsed time {time.perf_counter()-self.startTime:g}s - size {various.convert_size(self.filename.stat().st_size)}'
            )

    def getHandler(self)-> object:
        """
        Retrieves the file handler associated with the current instance.

        Returns:
            object: The file handler object.
        """
        return self.fhandle

    def write(self, 
              txt: Union[str, bytes])-> int:
        """
        Writes the given text or bytes to the file using the file handle.

        Args:
            txt (Union[str, bytes]): The text or bytes to be written to the file.

        Returns:
            int: The number of characters or bytes written to the file.

        Raises:
            TypeError: If the input is neither a string nor bytes.
            ValueError: If the file handle is not writable or is closed.
        """
        return self.fhandle.write(txt)

    def fixRight(self, 
                 append: Optional[bool]=None, 
                 right: Optional[str]=None)-> None:
        """
        Adjusts the file writing mode and append behavior.

        This method sets or updates the file writing mode (`self.right`) and 
        the append behavior (`self.append`) based on the provided arguments.

        Args:
            append (Optional[bool]): If specified, determines whether to append 
                to the file (`True`) or overwrite it (`False`). Overrides `right` 
                if provided.
            right (Optional[str]): A string indicating the file mode. Typically 
                'w' for write or 'a' for append. If provided, it determines the 
                append behavior unless `append` is explicitly set.

        Raises:
            TypeError: If `right` is provided but is not a string or does not 
                start with 'w' or 'a'.
        """ 
        if append is not None:
            self.append = append
            if append:
                self.right = 'a'
            else:
                self.right = 'w'
        else:
            self.right = right
            if right[0] == 'w':
                self.append = False
            elif right[0] == 'a':
                self.append = True
