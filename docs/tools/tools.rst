Command Line Tools
===================

With all tools, the library will attempt to autodetect the payload format
being used by the VI. If it's not sending any messages this is not possible, so
you may need to provide the current payload format explicitly with the
``--format`` flag. For example, here's a command to change the
passthrough status of bus 1, but with the payload format for the request
explicitly set the protocol buffers:

.. code-block:: bash

    $ openxc-control set --bus 1 --passthrough --format protobuf

The following links describe the available openxc-python commands.

.. toctree::
    :maxdepth: 1
    :glob:

    *
