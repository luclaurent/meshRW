"""
Various useful tools
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""

import time

import numpy
from loguru import logger as Logger


def convert_size(size_bytes):
    """
    Convert size in bytes to human readable size
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(numpy.floor(numpy.log(size_bytes)/numpy.log(1024)))
    p = numpy.power(1024, i)
    s = round(size_bytes / p, 2)
    return f'{s:g} {size_name[i]}'

# decorator to measure time
def timeit(txt=None):
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
