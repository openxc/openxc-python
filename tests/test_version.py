
"""
@file    openxc-python\tests\test_version.py OpenXC Test Version Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   OpenXC Test Version Script."""

from nose.tools import eq_

import openxc.version


def test_get_version():
    """Test Get Version Routine"""
    version = openxc.version.get_version()
    eq_(type(version), str)
