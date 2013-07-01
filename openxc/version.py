
"""
@file    openxc-python\openxc\version.py OpenXC Version Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   Current OpenXC version constant.

         This functionality is contained in its own module to prevent circular 
         import problems with ``__init__.py`` (which is loaded by setup.py 
         during installation, which in turn needs access to this version 
         information.)"""

## @var VERSION
# Version number stored as a comma-separated entry
VERSION = (0, 9, 4)

## @var __version__
# OpenXC-Python version string
__version__ = '.'.join(map(str, VERSION))

def get_version():
    """Returns current OpenXC-Python version."""
    return __version__
