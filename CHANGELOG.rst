OpenXC Python Library Changelog
===============================

v0.9.5-dev
----------

* Updated to work with v5.x of VI firmware.
* Default to inverted bit mapping for code generation only if using a
  database-backed mapping.

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
