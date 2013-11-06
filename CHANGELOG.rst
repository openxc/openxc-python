OpenXC Python Library Changelog
===============================

v0.10.2-dev
----------

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
