=====================================
``openxc-gps`` options and arguments
=====================================

:program:`openxc-gps` is a command-line tool to convert a raw OpenXC data stream
that includes GPS information (namely latitude and longitude) into one of a few
popular formats for GPS traces. The output file is printed to `stdout`, so the
output must be redirected to save it to a file.

The only format currently supported is `.gpx`, which can be imported by
Google Earth, the Google Maps API and many other popular tools.

Basic use
=========

Convert a previously recorded OpenXC JSON trace file to GPX:

.. code-block:: bash

    $ openxc-gps --trace trace.json > trace.gpx

Convert a real-time stream from a USB vehicle interface to GPX in real-time (using
all defaults, and printing to `stdout`):

.. code-block:: bash

    $ openxc-gps

Command-line options
====================

An overview of all possible command line options can be found via
``--help``.
