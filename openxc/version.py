"""
Current OpenXC version constant.

This functionality is contained in its own module to prevent circular import
problems with ``__init__.py`` (which is loaded by setup.py during installation,
which in turn needs access to this version information.)
"""

VERSION = (0, 11, 2)

__version__ = '.'.join(map(str, VERSION))

def get_version():
    return __version__
