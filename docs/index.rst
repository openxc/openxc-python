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

To install using `pip`:

.. code-block:: sh

    $ [sudo] pip install -U openxc

To install using `easy_install`:

.. code-block:: sh

    $ [sudo] easy_install -U openxc

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

Serial Backend
--------------

If you intend to use the library with Python 3 and you want to connect to a CAN
translator via a USB-Serial or other UART connection, you must install the
`pyserial` Python library manually. There is an [outstanding
bug](https://github.com/openxc/openxc-python/issues/1) in the `pyserial` library
that blocks installation as a dependency in Python 3. It works fine if you
install it manually:

.. code-block:: sh

    $ [sudo] pip install pyserial


.. _usb:

USB Backend
-------------

If you intend to use the library to connect to a CAN translator via USB, you
must also install a native USB backend - `libusb-1.0` is the recommended library.

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

.. _`latest documentation`: http://openxcplatform.com/openxc-python
.. _`OpenXC site`: http://openxcplatform.com

Vehicle API Usage
-----------------

.. toctree::
    :maxdepth: 2
    :glob:

    usage/*

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

Development of `openxc-python` happens at `GitHub`_. Be sure to see our `contribution document`_ for details.

.. _`GitHub`: https://github.com/openxc/openxc-python
.. _`contribution document`: https://github.com/openxc/openxc-python/blob/master/CONTRIBUTING.mkd

Mailing list
------------

For discussions about the usage, development, and future of OpenXC, please join
the `OpenXC mailing list`_.

.. _`OpenXC mailing list`: http://groups.google.com/group/openxc

Bug tracker
------------

If you have any suggestions, bug reports or annoyances please report them
to our issue tracker at http://github.com/openxc/openxc-python/issues/
