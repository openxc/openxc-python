from nose.tools import eq_

import openxc.version


def test_get_version():
    """Test Get Version Routine"""
    version = openxc.version.get_version()
    eq_(type(version), str)
