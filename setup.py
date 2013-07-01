
"""
@file    openxc-python\setup.py Setup Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4
"""

import sys
from setuptools import setup, find_packages

from openxc.version import get_version

# This is a workaround for an odd exception that occurs when running the tests.
try:
    import multiprocessing
except ImportError:
    pass

## @var long_description
# Long description of this application.
long_description = open('README.rst').read()

## @var install_reqs
# Defines the required Python modules to install OpenXC-Python.
install_reqs = ['pyusb', 'units >= 0.5', 'argparse', 'requests==1.1.0',]


setup(
    ## @var name
    # The module name of this Python module, OpenXC-Python.
    name='openxc',
    ## @var version
    # The version of this Python module, OpenXC-Python.
    version=get_version(),
    ## @var description
    # The description of this Python module, OpenXC-Python.
    description='OpenXC is a platform for accessing vehicle data, and this is a library that is compatible with the CAN translator',
    ## @var long_description
    # The long description of this Python module, OpenXC-Python.
    long_description=long_description,
    ## @var author
    # Python module author(s)
    author='Christopher Peplin',
    ## @var author_email
    # Python module author(s) email address(es)
    author_email='cpeplin@ford.com',
    ## @var license
    # The software license applicable to this Python module, OpenXC-Python.
    license='BSD',
    ## @var classifiers
    # Software classifiers for this Python module, OpenXC-Python.
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    ## @var url
    # The Website URL associated with this Python package.
    url='http://github.com/openxc/openxc-python',
    ## @var packages
    # The packages included with this Python module, OpenXC-Python.
    packages=find_packages(exclude=["tests", "tests.*"]),
    ## @var package_data
    # Dictionary containing a key of packages and value list of related files.
    package_data={'openxc': ['generator/signals.cpp*']},
    ## @var test_suite
    # Defines the test suite.
    test_suite='nose.collector',
    ## @var tests_require
    # Defines the modules required to run the module tests.
    tests_require=['nose'],
    ## @var install_requires
    # Defines the Python modules required to install OpenXC-Python.
    install_requires=install_reqs,
    ## @var extras_require
    # Defines extra Python modules to utilize extra OpenXC-Python features.
    extras_require = {
        'serial': ["pyserial"],
        'lxml': ["lxml"],
    },
    ## @var entry_points
    # Module entry points
    entry_points={
        'console_scripts': [
            'openxc-dashboard = openxc.tools.dashboard:main',
            'openxc-dump = openxc.tools.dump:main',
            'openxc-control = openxc.tools.control:main',
            'openxc-gps = openxc.tools.gps:main',
            'openxc-trace-split = openxc.tools.tracesplit:main',
            'openxc-generate-firmware-code = openxc.tools.generate_code:main',
        ]
    },
)
