===================
OpenXC for Python
===================

.. image:: /_static/logo.png

:Version: 0.13.0
:Web: http://openxcplatform.com
:Download: http://pypi.python.org/pypi/openxc/
:Documentation: http://python.openxcplatform.com
:Source: http://github.com/openxc/openxc-python/

The OpenXC Python library (for Python 2.6 or 2.7) provides an interface to
vehicle data from the OpenXC Platform. The primary platform for OpenXC
applications is Android, but for prototyping and testing, often it is
preferrable to use a low-overhead environment like Python when developing.

In addition to a port of the Android library API, the package also contains a
number of command-line tools for connecting to the vehicle interface and
manipulating previously recorded vehicle data.

This Python package works with Python 2.6 and 2.7. Unfortunately we had to drop
support for Python 3 when we added the protobuf library as a dependency.

For general documentation on the OpenXC platform, visit the main `OpenXC site`_.

.. _`OpenXC site`: http://openxcplatform.com

.. toctree::
    :maxdepth: 1

    installation
    tools/tools
    example
    api/api
    contributing
