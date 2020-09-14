===============================================
OpenXC for Python
===============================================

.. image:: https://github.com/openxc/openxc-python/raw/master/docs/_static/logo.png

:Version: 2.1.0
:Web: http://openxcplatform.com
:Download: http://pypi.python.org/pypi/openxc/
:Documentation: http://python.openxcplatform.com
:Source: http://github.com/openxc/openxc-python/
:Keywords: vehicle, openxc, python

.. image:: https://travis-ci.org/openxc/openxc-python.svg?branch=master
    :target: https://travis-ci.org/openxc/openxc-python

.. image:: https://coveralls.io/repos/openxc/openxc-python/badge.png?branch=master
    :target: https://coveralls.io/r/openxc/openxc-python?branch=master

.. image:: https://readthedocs.org/projects/openxc-python-library/badge/
    :target: http://python.openxcplatform.com
    :alt: Documentation Status

The OpenXC Python library (for Python 3.6.7) provides an interface to
vehicle data from the OpenXC Platform. The primary platform for OpenXC
applications is Android, but for prototyping and testing, often it is
preferrable to use a low-overhead environment like Python when developing.

In addition to a port of the Android library API, the package also contains a
number of command-line tools for connecting to the CAN translator and
manipulating previously recorded vehicle data.

Due to changes in signals.cpp openxc-python Version 2.1.0 must be used with vi-firmware 8.1.0 or greater. 

To package run "setup.py sdist bdist_wheel"
to push to pypi run "python -m twine upload dist/\*"
Version files:

- CHANGELOG.rst
- README.rst
- openxc/version.py
- docs/index.rst

License
========

Copyright (c) 2012-2017 Ford Motor Company

Licensed under the BSD license.
