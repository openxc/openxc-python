=============================================
``openxc-generate-firmware-code`` - configure CAN messages, signals and buses
=============================================

The `OpenXC vehicle interface
firmware <http://vi-firmware.openxcplatform.com>`_ uses a JSON-formatted
configuration file to set up CAN messages, signals and buses. The configuration
options and many examples are included with the `VI firmware docs
<http://vi-firmware.openxcplatform.com/en/latest/config/config.html>`_. The
configuration file is used to generate C++ that is compiled with the open source
firmware.

The OpenXC Python library contains a command line tool,
``openxc-generate-firmware-code``, that can parse VI configuration files and
generate a proper C++ implementation to compile the VI firmware.

Once you've created a VI configuration file, run the
``openxc-generate-firmware-code`` tool to create an implementation of
the functions in the VI's ``signals.h``. In this example, the configuration is
in the file ``mycar.json``.

.. code-block:: sh

    $ openxc-generate-firmware-code --message-set mycar.json > signals.cpp
