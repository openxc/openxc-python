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

.. _`vi-firmware repository`: https://github.com/openxc/vi-windows-driver

Using the development version
-----------------------------

You can clone the repository and install the development version like so:

.. code-block:: sh

    $ git clone https://github.com/openxc/openxc-python
    $ cd openxc-python
    $ pip install -e .

Any time you update the clone of the Git repository, all of the Python tools
will be updated too.

