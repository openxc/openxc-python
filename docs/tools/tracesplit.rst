=====================================
``openxc-trace-split`` options and arguments
=====================================

:program:`openxc-trace-split` is a command-line tool to re-split a collection of
previously recorded OpenXC trace files by different units of time.

Often, trace files are recorded into arbitrarily sized chunks, e.g. a new trace
file every hour. The trace files are often most useful if grouped into more
logical chunks e.g. one "trip" in the vehicle.

This tool accepts a list of JSON trace files as arguments, reads them into
memory and sorts by time, then re-splits the file into new output files based on
the requested split unit. The unit is "trips" by default, which looks for gaps
of 5 minutes or more in the trace files to demarcate the trips.

The output files are named based on the timestamp of the first record recorded
in the segment.

Basic use
=========

Re-combine two trace files and re-split by trip (the default split unit)
instead of the original day splits:

.. code-block:: bash

    $ openxc-trace-split monday.json tuesday.json

Re-combine two trace files and re-split by hour instead of the original day
splits:

.. code-block:: bash

    $ openxc-trace-split --split hour monday.json tuesday.json

Re-split an entire directory of JSON files by trip

.. code-block:: bash

    $ openxc-trace-split *.json

Command-line options
====================

A quick overview of all possible command line options can be found via
``--help``.

.. cmdoption:: -s, --split <unit>

    Change the time unit used to split trace files - choices are ``day``,
    ``hour`` and ``trip``. The default unit is ``trip``, which looks for large
    gaps of time in the trace files where no data was recorded.
