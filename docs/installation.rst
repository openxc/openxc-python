Installation
============

Install Python and Pip
----------------------

This library (obviously) requires a Python language runtime - the OpenXC library
currently works with Python 2.6 and 2.7, but not Python 3.x.

- **Mac OS X and Linux**

   Mac OS X and most Linux distributions already have a compatible Python
   installed. Run ``python --version`` from a terminal to check - you need a
   2.7.x version, such as 2.7.8.

- **Windows**

   #. Download and run the [Python 2.7.x MSI
      installer](https://www.python.org/download/releases/2.7.8/). Make sure to
      select to option to ``Add python.exe to Path``.
   #. Add the Python Scripts directory your PATH:
      ``PATH=%PATH%;c:\Python27\Scripts``. If you aren't sure how to edit your
      ``PATH``, see `this guide for all versions of Windows
      <https://www.java.com/en/download/help/path.xml>`_. Log out and back in for
      the change to take effect.
   #. Install [pip](https://pip.pypa.io/en/latest/installing.html#install-pip), a
      Python package manager by saving the ``get-pip.py`` script to a file and
      running it from a terminal.

- **Cygwin**

   From the ``setup.exe`` package list, select the ``python`` and
   ``python-setuptools`` packages. Then, inside Cygwin install ``pip`` using
   ``easy_install``:

   .. code-block:: sh

       $ easy_install pip

Install the openxc Package
--------------------------

You can install or upgrade the OpenXC library from the Python Package Index (PyPI) with
``pip`` at the command line:

.. code-block:: sh

    $ [sudo] pip install -U openxc

.. _usb:

USB Backend
-------------

If you intend to use the library to connect to a vehicle interface via USB, you
must also install a native USB backend - ``libusb-1.0`` is the recommended
library.

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

- **Windows**

    Download and install the `OpenXC VI USB driver`_. You must install the
    driver manually through the Device Manager while the VI is plugged in and
    on - either running the emulator firmware so it never turns off, or plugged
    into a real car.

- **Cygwin**

    Install the VI USB driver as in a regular Windows installation.

    If you get the error ``Skipping USB device: [Errno 88] Operation not
    supported or unimplemented on this platform`` when you run any of the OpenXC
    Python tools, make sure you **do not** have the ``libusb`` Cygwin package
    installed - that is explicitly not compatible.

.. _`OpenXC VI USB driver`: https://github.com/openxc/vi-windows-driver

Using the development version
-----------------------------

You can clone the repository and install the development version like so:

.. code-block:: sh

    $ git clone https://github.com/openxc/openxc-python
    $ cd openxc-python
    $ pip install -e .

Any time you update the clone of the Git repository, all of the Python tools
will be updated too.

