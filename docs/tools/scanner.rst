========================================================================
``openxc-scanner`` - scanner for determining support diagnostic requests
========================================================================

:program:`openxc-scanner` is a is a rudimentary diagnostic scanner that can give
you a high level view of the what message IDs are used by modules on a vehicle
network and to which diagnostics services they (potentially) respond.

When you run ``openxc-scanner``, it will send a Tester Present diagnostic
request to all possible 11-bit CAN message IDs (or arbitration IDs). For each
module that responds, it then sends a blank request for each possible diagnostic
service to the module's arbitration ID. Finally, for each service that
responded, it fuzzes the payload field to see if anything interesting can
happen.

Make sure you do not run this tool while operating your car. The Tester Present
message can put modules into diagnostic modes that aren't safe for driving, or
other unexpected behaviors may occur (e.g. your powered driver's seat may reset
the position, or the powered trunk may open up).

Basic use
=========

There's not much to it, just run it and view the results. It may take a number
of minutes to complete the scan if there are many active modules.

.. code-block:: bash

    $ openxc-scanner

Scanning a specific message ID
==============================

If you wish to scan only a single message ID, you can skip right to it:

.. code-block:: bash

    $ openxc-scanner --message-id 0x7e0

Command-line options
====================

A description overview of all possible command line options can be found via
``--help``.
