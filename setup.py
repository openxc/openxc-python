import sys
from setuptools import setup, find_packages

from openxc.version import get_version

# This is a workaround for an odd exception that occurs when running the tests.
try:
    import multiprocessing
except ImportError:
    pass

long_description = open('README.rst').read()

install_reqs = ['pyusb', 'units >= 0.5', 'requests==0.14.1', 'argparse',]

if sys.version_info < (3, 0):
    install_reqs.append('pyserial')

setup(name='openxc',
    version=get_version(),
    description='OpenXC is a platform for accessing vehicle data, and this is a library that is compatible with the CAN translator',
    long_description=long_description,
    author='Christopher Peplin',
    author_email='cpeplin@ford.com',
    license='BSD',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    url='http://github.com/openxc/openxc-python',
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=install_reqs,
    entry_points={
        'console_scripts': [
            'openxc-dashboard = openxc.tools.dashboard:main',
            'openxc-dump = openxc.tools.dump:main',
            'openxc-control = openxc.tools.control:main',
            'openxc-gps = openxc.tools.gps:main',
            'openxc-trace-split = openxc.tools.tracesplit:main',
        ]
    },
)
