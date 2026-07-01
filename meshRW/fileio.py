"""
This file is part of the meshRW package
---
This file includes the definition and tools to manipulate files
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""
# pylint: disable=unspecified-encoding
from typing import IO, Optional, Union, cast
import gzip
import bz2 as bz2lib
import time
from pathlib import Path

from loguru import logger as Logger

from . import various


class FileHandler:
    """
    FileHandler is a class designed to handle file operations with support for 
    compression, safe mode, and flexible file access rights. It provides methods 
    to open, write, and close files while ensuring proper error handling and logging.

        right (str): The mode used to open the file ('r', 'w', 'a', etc.).

    Methods:
        __init__(filename: Union[str, Path]=None, append: Optional[bool]=None, 
                 right: str='w', gz: bool=False, bz2: bool=False, 
                 safe_mode: bool=False) -> None:
            Initializes the FileHandler class with the specified parameters.

        get_filename(filename: Path, gz: bool=False, bz2: bool=False) -> None:
            Determines the appropriate filename and compression type based on the 
            provided file path and optional compression flags.

        open(safe_mode: bool=False) -> object:

        close() -> None:
            Closes the currently opened file and logs information about the file.

        get_handler() -> object:

        write(txt: Union[str, bytes]) -> int:

        fix_right(append: Optional[bool]=None, right: Optional[str]=None) -> None:
            Adjusts the file writing mode and append behavior based on the provided 
            arguments.

        ValueError: If 'filename' is not provided or if neither 'right' nor 'append' 
                    is specified during initialization.
        FileExistsError: If safe mode is enabled and the file already exists.
        TypeError: If invalid types are provided for certain arguments.
        AttributeError: If attempting to close a file without a valid file handle.
    """

    def __init__(self,
                filename: Union[str, Path, None]=None,
                append: Optional[bool|None]=None,
                right: str='w',
                flag_gz: bool=False,
                flag_bz2: bool=False,
                safe_mode: bool=False)-> None:
        """
        Initializes the file handling class.

        Args:
            filename (Union[str, Path], optional): Name of the file to open. Defaults to None.
            append (Optional[bool], optional): If True, appends to an existing file 
            (overrides 'right'). Defaults to None.
            right (str, optional): Specifies the mode to open the file ('r', 'a', 'w', etc.). 
            Defaults to 'w'.
            flag_gz (bool, optional): If True, enables on-the-fly compression with gzip.
            Defaults to False.
            flag_bz2 (bool, optional): If True, enables on-the-fly compression with bzip2. 
            Defaults to False.
            safe_mode (bool, optional): If True, prevents overwriting of existing files. 
            Defaults to False.

        Attributes:
            filename (Optional[Path]): The resolved file path.
            dirname (Optional[Path]): The directory of the file.
            fhandle (Optional[IO]): The file handle for the opened file.
            right (str): The mode used to open the file.
            append (Optional[bool]): Indicates if the file is opened in append mode.
            compress (Optional[str]): The compression method used ('gz', 'bz2', or None).
            start_time (float): The timestamp when the file operation starts.

        Raises:
            ValueError: If 'filename' is not provided or if neither 'right' nor 'append' 
            is specified.
        """
        self.filename = None
        self.dirname = None
        self.fhandle = None
        self.right: str = right
        self.append = None
        self.compress = None
        self.start_time = 0
        #
        self.fix_right(append=append, right=right)

        # check arguments
        if not filename:
            Logger.error('Filename argument missing')
        if not right and not append:
            Logger.error('Right(s) not provided')
        # load the filename
        if filename is not None:
            self.get_filename(Path(filename), flag_gz=flag_gz, flag_bz2=flag_bz2)
        # open the file
        self.open(safe_mode)

    def get_filename(self, filename: Path, flag_gz: bool=False, flag_bz2: bool=False)-> None:
        """
        Determines the appropriate filename and compression type based on the provided
        file path and optional compression flags.

        Args:
            filename (Path): The input file path.
            flag_gz (bool, optional): If True, appends a '.gz' extension to the filename 
                if no compression is detected. Defaults to False.
            flag_bz2 (bool, optional): If True, appends a '.bz2' extension to the filename 
                if no compression is detected. Defaults to False.

        Attributes Set:
            self.compress (str or None): The compression type ('gz', 'bz2', or None).
            self.basename (str): The name of the file (including extension).
            self.dirname (Path): The absolute parent directory of the file.
            self.filename (Path): The full file path.

        Notes:
            - If the file already has a '.gz' or '.bz2' extension, the corresponding 
              compression type is set, and the filename remains unchanged.
            - If no compression is detected and `flag_gz` or `flag_bz2` is True, the respective 
              extension is appended to the filename, and the compression type is set.
        """
        self.compress = None
        # check extension for compression
        if filename.suffix == '.gz':
            self.compress = 'gz'
        elif filename.suffix == '.bz2':
            self.compress = 'bz2'
        elif flag_gz:
            filename.with_suffix(filename.suffix + '.gz')
            self.compress = 'gz'
        elif flag_bz2:
            filename.with_suffix(filename.suffix + '.bz2')
            self.compress = 'bz2'
        # extract information about filename
        self.basename = filename.name
        self.dirname = filename.absolute().parent
        self.filename = filename

    def open(self, safe_mode: bool=False) -> Optional[object]:
        """
        Opens a file with specified access rights and optional safe mode.

        Parameters:
            safe_mode (bool): If True, prevents overwriting an existing file. 
                             Defaults to False.

        Returns:
            object: A file handle to the opened file.

        Behavior:
            - If `append` mode is enabled and the file does not exist, logs a warning 
              and adjusts the access rights to disable append mode.
            - If `safe_mode` is True and the file exists, prevents overwriting and logs a warning.
            - If `safe_mode` is False and the file exists, allows overwriting and logs a warning.
            - Supports opening files with optional compression (`gz` or `bz2`).
            - Logs debug information about the file opening process.
            - Records the timestamp when the file is opened.
        """
        if not self.filename:
            Logger.error('Filename argument missing')
            return None
        # adapt the rights (in case of the file does not exist)
        if self.append and not self.filename.exists():
            Logger.warning(f'{self.basename} does not exist! Unable to append')
            self.fix_right(append=False)
        if not safe_mode and self.filename.exists() and not self.append and 'w' in self.right:
            Logger.warning(f'{self.basename} already exists! It will be overwritten')
        if safe_mode and self.filename.exists() and not self.append and 'w' in self.right:
            Logger.error(f'{self.basename} already exists! Not overwrite it')
            raise FileExistsError
        else:
            #
            Logger.debug(f'Open {self.basename} in {self.dirname} with right {self.right}')
            # open file
            if self.compress == 'gz':
                Logger.debug('Use GZ lib')

                if 'b' in self.right:
                    self.fhandle = gzip.open(self.filename, self.right)
                else:
                    self.fhandle = gzip.open(self.filename, self.right, encoding='utf-8')
            elif self.compress == 'bz2':
                Logger.debug('Use BZ2 lib')

                if 'b' in self.right:
                    self.fhandle = bz2lib.open(self.filename, self.right)
                else:
                    self.fhandle = bz2lib.open(self.filename, self.right, encoding='utf-8')
            else:
                if 'b' in self.right:
                    self.fhandle = self.filename.open(mode=self.right)
                else:
                    self.fhandle = self.filename.open(mode=self.right, encoding='utf-8')
        # store timestamp at opening
        self.start_time = time.perf_counter()
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
        if self.fhandle and self.filename:
            self.fhandle.close()
            self.fhandle = None
            txt = f'Close file {self.basename} with elapsed time '
            txt += f'{time.perf_counter()-self.start_time:g}s'
            txt += f'- size {various.convert_size(self.filename.stat().st_size)}'
            Logger.info(txt)

    def get_handler(self)-> object:
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
        if not self.fhandle:
            Logger.error('File handle is not writable or is closed')
            raise ValueError('File handle is not writable or is closed')

        if isinstance(txt, bytes):
            if 'b' not in self.right:
                raise TypeError('Binary data requires a binary file mode')
            return cast(IO[bytes], self.fhandle).write(txt)

        if isinstance(txt, str):
            if 'b' in self.right:
                raise TypeError('Text data requires a text file mode')
            return cast(IO[str], self.fhandle).write(txt)

        raise TypeError('Only str and bytes are supported')

    def fix_right(self,
                 append: Optional[bool]=None,
                 right: Optional[str]='')-> None:
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
            resolved_right = right or ''
            self.right = resolved_right
            if len(resolved_right) > 0:
                if resolved_right[0] == 'w':
                    self.append = False
                elif resolved_right[0] == 'a':
                    self.append = True


class fileHandler(FileHandler):
    """Backward-compatible alias for :class:`FileHandler`.

    Supports legacy keyword arguments ``gz``, ``bz2`` and ``safeMode``.
    """

    def __init__(
        self,
        filename: Union[str, Path, None] = None,
        append: Optional[bool] = None,
        right: str = 'w',
        gz: bool = False,
        bz2: bool = False,
        safeMode: bool = False,
        **kwargs: object,
    ) -> None:
        super().__init__(
            filename=filename,
            append=append,
            right=right,
            flag_gz=gz,
            flag_bz2=bz2,
            safe_mode=safeMode,
            **kwargs,
        )

    def getHandler(self) -> object:
        """Compatibility wrapper for :meth:`get_handler`."""
        return self.get_handler()
