=============================================
OpenXC for Python
=============================================

About
=====

.. include:: ../README.rst

This Python package works with Python 2.6 and 2.7. Unfortunately we had to drop
support for Python 3 when we added the protobuf library as a dependency.

Installation
============

You can install the OpenXC library from the Python Package Index (PyPI) with
``easy_install`` or ``pip`` at the command line:

To install using ``pip``:

.. code-block:: sh

    $ [sudo] pip install -U openxc

If you are using Cygwin in Windows, select the ``python`` and
``python-setuptools`` packages from the Cygwin installer and then use
``easy_install`` to grab the OpenXC library:

.. code-block:: sh

    $ [sudo] easy_install -U openxc

If you plan to connect to a vehicle interface via USB, you will also need to
install a :ref:`USB backend <usb>`.

.. _usb:

USB Backend
-------------

If you intend to use the library to connect to a vehicle interface via USB, you
must also install a native USB backend - ``libusb-1.0`` is the recommended
library (it's called ``libusb-win32`` on Cygwin - **don't install** ``libusb``).

- **Mac OS X**

    First install Homebrew_, then run::

        $ brew install libusb

.. _Homebrew: http://mxcl.github.com/homebrew/

- **Ubuntu**

    ``libusb`` is available in the main repository::

        $ sudo apt-get install libusb-1.0-0

- **Arch Linux**

    Install ``libusb`` using ``pacman``::

        $ sudo pacman -S libusbx

- **Cygwin in Windows**

    Install ``libusb-win32`` from the Cygwin ``setup.exe`` and the USB driver
    from the `vi-firmware repository`_. If you get the error ``Skipping USB
    device: [Errno 88] Operation not supported or unimplemented on this
    platform`` when you run any of the OpenXC Python tools, make sure you **do
    not** have the ``libusb`` package installed as well - that one is explicitly
    not compatible.

.. _`vi-firmware repository`: https://github.com/openxc/vi-firmware/tree/master/conf/windows-driver

Using the development version
-----------------------------

You can clone the repository and install the development version like so:

.. code-block:: sh

    $ git clone https://github.com/openxc/openxc-python
    $ cd openxc-python
    $ pip install -e .

Any time you update the clone if the Git repository, all of the Python tools
will be updated too.

Documentation
=============

The `latest documentation`_ with user guides, tutorials and API reference
is hosted at Read The Docs. For general documentation on the OpenXC platform,
visit the main `OpenXC site`_.


.. _`latest documentation`: http://openxcplatform.com/openxc-python
.. _`OpenXC site`: http://openxcplatform.com

VI Firmware Code Generation
----------------------------

For information on the code generation tools for the `OpenXC vehicle interface
firmware <http://vi-firmware.openxcplatform.com>`_ (previous a part of the
`vi-firmware <https://github.com/openxc/vi-firmware>`_ repository), see the
:doc:`code generation documentation <code-generation>`.

.. toctree::
    :maxdepth: 2

    code-generation
    config-examples
    config-write-examples

Tools
------

.. toctree::
    :maxdepth: 2
    :glob:

    tools/*

Vehicle API Reference
---------------------

.. toctree::
    :maxdepth: 1
    :glob:

    api/*

Contributing
============

Development of ``openxc-python`` happens at `GitHub`_. Be sure to see our `contribution document`_ for details.

.. _`GitHub`: https://github.com/openxc/openxc-python
.. _`contribution document`: https://github.com/openxc/openxc-python/blob/master/CONTRIBUTING.rst

Test Suite
----------

The ``openxc-python`` repository contains a test suite that can be run with the
``tox`` tool, which attemps to run the test suite in Python 2.7. If
you wish to just run the test suite in your primary Python version, run

.. code-block:: sh

    $ python setup.py test

To run it with tox:

.. code-block:: sh

    $ tox

Mailing list
------------

For discussions about the usage, development, and future of OpenXC, please join
the `OpenXC mailing list`_.

.. _`OpenXC mailing list`: http://groups.google.com/group/openxc

Bug tracker
------------

If you have any suggestions, bug reports or annoyances please report them
to our issue tracker at http://github.com/openxc/openxc-python/issues/
