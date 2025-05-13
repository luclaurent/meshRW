"""
This file is part of the meshRW package
---
Various useful tools
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""

import time
from typing import Union, Optional, Callable

import numpy
from loguru import logger as Logger


def convert_size(size_bytes: Union[int, float]) -> str:
    """
    Convert a size in bytes to a human-readable string format.

    This function takes a size in bytes (as an integer or float) and converts it 
    to a more human-readable format using appropriate units (e.g., KB, MB, GB, etc.).

    Args:
        size_bytes (Union[int, float]): The size in bytes to be converted.

    Returns:
        str: A human-readable string representation of the size, including the 
             appropriate unit (e.g., '1.5 MB', '200 KB').

    Raises:
        ValueError: If the input size_bytes is negative.

    Examples:
        >>> convert_size(1024)
        '1 KB'
        >>> convert_size(1048576)
        '1 MB'
        >>> convert_size(0)
        '0B'
    """
    if size_bytes == 0:
        return '0B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(numpy.floor(numpy.log(size_bytes) / numpy.log(1024)))
    p = numpy.power(1024, i)
    s = round(size_bytes / p, 2)
    return f'{s:g} {size_name[i]}'


# decorator to measure time
def timeit(txt: Optional[str] = None)-> Callable:
    """
    A decorator to measure and log the execution time of a function.

    Args:
        txt (Optional[str]): An optional string to include in the log message. 
                                If provided, it will be prefixed to the execution time.

    Returns:
        Callable: The decorated function with execution time measurement.

    Usage:
        @timeit("My Function")
        def my_function():
            # Function implementation
            pass

    The execution time will be logged using the `Logger.debug` method.
    """
    def decorator(func):
        def timeit_wrapper(*args, **kwargs):

            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            # first item in the args, ie `args[0]` is `self`
            if txt is not None:
                Logger.debug(f'{txt} - {total_time:.4f} s')
            else:
                Logger.debug(f'Execution time: {total_time:.4f} s')
            return result

        return timeit_wrapper

    return decorator
