Welcome to OpenXC for Python's documentation!
=============================================

About
=====

.. include:: ../README.rst

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
-------------

If you intend to use the library to connect to a CAN translator via USB, you
must also install a native USB backend - `libusb-1.0` is the reccomend library.

- **Mac OS X**

    First install homebrew_, then run::

        $ brew install libusb

.. _homebrew: http://mxcl.github.com/homebrew/

- **Ubuntu**

    `libusb` is available in the main repository::

        $ sudo apt-get install libusb-1.0-0

- **Arch Linux**

    Install `libusb` using `pacman`::

        $ sudo pacman -S libusbx

Documentation
=============

The `latest documentation`_ with user guides, tutorials and API reference
is hosted at Read The Docs. For general documentation on the OpenXC platform,
visit the main `OpenXC site`_.

.. _`latest documentation`: http://TODO/readthedocs
.. _`OpenXC site`: http://openxcplatform.com

.. toctree::
    :hidden:

    api
    tools

Vehicle API
-----------

.. toctree::
    :maxdepth: 1
    :glob:

    api/*

Tools
------

.. toctree::
    :maxdepth: 2
    :glob:

    tools/*

Getting Help
============

Mailing list
------------

For discussions about the usage, development, and future of OpenXC, please join
the `OpenXC mailing list`_.

.. _`OpenXC mailing list`: http://groups.google.com/group/openxc

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
