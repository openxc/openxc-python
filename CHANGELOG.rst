OpenXC Python Library Changelog
===============================

v0.14.0
----------

* Fix: Remove support for Python 2.6
* Fix: Diagnostic response cleanup
* Feature: Add "platform" command support
* Fix: Documentation improvements
* Fix: openxc-dump command file access

v0.13.0
----------

* Feature: Support for new C5 Cellular, SD, and RTC commands

v0.12.0
-----------

* Feature: Support scanning for Bluetooth devices when using Linux
* Feature: Support connecting to Bluetooth VIs directly from the library in
  Linux using BlueZ.
* Feature: Support adding and cancelling diagnostic requests.
* Feature: Read 'status' field in command responses.
* Feature: Allow explicitly setting the payload format when sending and
  receiving commands with a VI.
* Feature: Support command to control status of CAN acceptance filter bypass.
* Feature: Support controlling passthrough status of CAN buses in VI.
* Feature: Support 'loopback' attribute of CAN buses in firmware config.
* Feature: Support setting desired decoding type for diagnostic requests.
* Feature: Support command to change payload format of VI.
* Improvement: Better balance between big efficient reads and quick signal
  responses when receiving via USB.
* Improvement: Remove now unnecessary sleep from command line tools.
* Improvement: Complete full support for protobuf message deserialization.
* Improvement: Improve unit test coverage from 27% to 58%.
* Fix: Use correct abbreviation for kilometer unit.
* Fix: Remove deprecated signal attribute from example code.
* Fix: Spool up message receivers before sending requests to make sure not to
  miss responses.

v0.11.3
----------

* Remove embedded platform-specific code from generated signals file for
  firmware (to match vi-firmware v6.0.2).
* Add documentation on installing in Windows without Cygwin.

v0.11.2
----------

* Fixed parsing of v6.x style OpenXC messages from a network data source.
* Fixed use of const variables in generated code.
* Fixed a code gen. regression where custom C++ functions were called before
  being declared / defined.
* Include OBD2 message handler in generated code so it can be used as a handler
  without custom source code files.
* Don't require a working network connection and DNS to run the test suite.

v0.11.1
----------

* Fixed receiving data from new network based VI using null delimiters
* Make sure const variables are initialized in generated firmware code.

v0.11
----------

* Support communicating with vi-firmware v6.x.
* Support generating code for vi-firmware v6.x.
* Support control commands over serial in additional to USB (version, device ID
  diagnostics, raw CAN messages).
* Read debug log data over USB from a VI (see the `log-mode` flag on the CLI
  tools).
* Support diagnostic request/response exchange with a v6.x VI.
* Add `openxc-diag`, `openxc-scanner` and `openxc-obd2scanner` CLI tools.
* Increase Bluetooth VI connection reliabilty when sending commands.

v0.10.3
----------

* In generated code, include the extra sources after messages and signals so
  they are already defined.

v0.10.2
----------

* Fix bit_numbering_inverted flag override in code generation.
* Fix using only 1 CAN bus with code generation.

v0.10.1
----------

* Rename and supported 'raw_writable' flag on CAN bus in VI configuration.

v0.10
----------

* Dropped support for Python 3 - needed to add protobuf dependency, which
  doesn't work with Python 3 yet.
* Significant speedup in VI firmware code generation with simple parsed XML
  caching
* Parse binary output payload from a vehicle interface (experimental)
* Small bug fixes and efficiency improvements with code generation.

v0.9.5
----------

* Improve screen width detection in openxc-dashboard
* Add veritcal keyboard scrolling to openxc-dashboard
* Support displaying raw CAN messages in openxc-dashboard
* Allow registering a listener for all measurements
* Fix non-looping trace file playback
* Allow playing back raw CAN trace files.
* Updated to work with v5.x of VI firmware.
  * Allow a message to have multiple handlers
  * Fix a bug that disallowed ignoring a signal with states defined
  * Add max_message_frequency and force_send_changed_signals to messages
  * Add max_frequency and force_send_changed to signals
  * Allow overriding bit inversion on a per-signal basis
  * Define as many things const as possible to save memory in VI
  * Add 'unfiltered' and 'filtered' raw CAN modes
  * Allow setting max CAN message freq for all buses.
  * Default to inverted bit mapping only if using a database-backed mapping.

v0.9.4
----------

* Move vehicle interface code generation utilites from cantranslator repository
  to this Python library
* Support playing back a raw CAN trace file at the same speed it was recorded.

v0.9.3
------

* Fix openxc-dashboard in Python 3.3.
* Increase robustness to invalid messages.
* Update pre-programmed OpenXC signals to match v4.0 release of the OpenXC
  vehicle interface (VI).
* Match defaut serial baud rate to v4.0 release of OpenXC VI
* Other small bug fixes and improvements.

v0.9.2
------

Botched this release.

v0.9.1
------

* Make pyserial an optional dependency to work around an issue with that package
  in Python 3

v0.9
----

* Initial release
