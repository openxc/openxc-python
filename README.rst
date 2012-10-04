=================================
openxc - Python Library for the OpenXC Platform
====================

.. image:: http://TODO/openxc/logo

:Version: 0.9 (DEVEL)
:Web: http://openxcplatform.com
:Download: http://pypi.python.org/pypi/openxc/
:Source: http://github.com/openxc/openxc-python/
:Keywords: vehicle, openxc, python

--

The OpenXC Python library (for Python 2.6 or higher) provides an alternative
interface to vehicle data from the OpenXC Platform. The primary platform for
OpenXC applications is Android, but for prototyping and testing, often it is
preferrable to use a low-overhead environment like Python when developing.

In addition to a port of the Android library API, the package also contains a
number of command-line tools for connecting to the CAN translator and
manipulating previously recorded vehicle data.

Documentation
=============

The `latest documentation`_ with user guides, tutorials and API reference
is hosted at Read The Docs. For general documentation on the OpenXC platform,
visit the main `OpenXC site`_.

.. _`latest documentation`: http://TODO/readthedocs
.. _`OpenXC site`: http://openxcplatform.com

Installation
============

You can install OpenXC either via the Python Package Index (PyPI) or from
source.

To install using `pip`,::

    $ pip install -U openxc

To install using `easy_install`,::

    $ easy_install -U openxc

Downloading and installing from source
--------------------------------------

Download the latest version of the OpenXC Python library from
http://pypi.python.org/pypi/openxc/

You can install it by doing the following,::

    $ tar xvfz openxc-0.0.0.tar.gz
    $ cd openxc-0.0.0
    $ python setup.py build
    # python setup.py install

The last command must be executed as a privileged user if you are not currently
using a virtualenv.

Using the development version
-----------------------------

You can clone the repository by doing the following::

    $ git clone https://github.com/openxc/openxc-python
    $ cd openxc-python
    $ python setup.py develop

USB Backend
==============

If you intend to use the library to connect to a CAN translator via USB, you
must also install a native USB backend - `libusb-1.0` is the reccomend library.

- **Mac OS X**

    First install homebrew_, then run::

        $ brew install libusb

.. _homebrew: http://mxcl.github.com/homebrew/

- **Ubuntu**

    ::
        $ sudo apt-get install libusb-1.0-0

- **Arch Linux**

    ::
        $ sudo pacman -S libusbx

Getting Help
============

Mailing list
------------

For discussions about the usage, development, and future of OpenXC, please join
the `openxc mailing list`_.

.. _`openxc mailing list`: http://groups.google.com/group/openxc

Bug tracker
------------

If you have any suggestions, bug reports or annoyances please report them
to our issue tracker at http://github.com/openxc/openxc-python/issues/

Contributing
============

Development of `openxc-python` happens at `GitHub`_. Be sure to see our `contribution document`_ for details.

.. _`GitHub`: https://github.com/openxc/openxc-python
.. _`contribution document`: https://github.com/openxc/openxc-android/blob/master/CONTRIBUTING.mkd

License
=======

Copyright (c) 2012-2013 Ford Motor Company
Licensed under the BSD license.
