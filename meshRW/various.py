"""
Various useful tools
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""

import numpy


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
    return '{:g} {}'.format(s, size_name[i])