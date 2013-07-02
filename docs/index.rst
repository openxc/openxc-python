=============================================
OpenXC for Python
=============================================

About
=====

.. include:: ../README.rst

Installation
============

You can install OpenXC either via the Python Package Index (PyPI) or from
source. You will also need to install a :ref:`USB backend <usb>`.

To install using ``pip``:

.. code-block:: sh

    $ [sudo] pip install -U openxc

If you are using Cygwin, install the ``python`` and ``python-setuptools``
packages and then you can run:

.. code-block:: sh

    $ [sudo] easy_install -U openxc

.. _usb:

USB Backend
-------------

If you intend to use the library to connect to a CAN translator via USB, you
must also install a native USB backend - ``libusb-1.0`` is the recommended library.

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
    from the `cantranslator repository`_.

.. _`cantranslator repository`: https://github.com/openxc/cantranslator/tree/master/conf/windows-driver

Serial Backend
--------------

If you intend to use the library with Python 3 and you want to connect to a CAN
translator via a USB-Serial or other UART connection, you must install the
``pyserial`` Python library manually. There is an [outstanding
bug](https://github.com/openxc/openxc-python/issues/1) in the ``pyserial`` library
that blocks installation as a dependency in Python 3. It works fine if you
install it manually:

.. code-block:: sh

    $ [sudo] pip install pyserial

Downloading and installing from source
--------------------------------------

Download the latest version of the OpenXC Python library from
http://pypi.python.org/pypi/openxc/

You can install it by doing the following

.. code-block:: sh

    $ tar xvfz openxc-0.0.0.tar.gz
    $ cd openxc-0.0.0
    $ python setup.py build
    # python setup.py install

The last command must be executed as a privileged user if you are not currently
using a virtualenv.

Using the development version
-----------------------------

You can clone the repository by doing the following

.. code-block:: sh

    $ git clone https://github.com/openxc/openxc-python
    $ cd openxc-python
    $ python setup.py develop


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
`cantranslator <https://github.com/openxc/cantranslator>`_ repository), see the
:doc:`code generation documentation <code-generation>`.

.. toctree::
    :maxdepth: 2

    code-generation

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
``tox`` tool, which attemps to run the test suite in Python 2.6, 2.7 and 3.3. If
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
