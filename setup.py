import sys
from setuptools import setup, find_packages

from openxc.version import get_version

# This is a workaround for an odd exception that occurs when running the tests.
try:
    import multiprocessing
except ImportError:
    pass

long_description = open('README.rst').read()

install_reqs = ['pyusb==1.0.0a3', 'units >= 0.5', 'argparse', 'requests==2.20.0',
        'protobuf==2.6.1'] + ["windows-curses >= 1.1"] if "win" in sys.platform else [],

setup(name='openxc',
    version=get_version(),
    description='A Python library to connect to an OpenXC vehicle interface',
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
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={'openxc': ['generator/signals.cpp*']},
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=install_reqs,
    extras_require = {
        'serial': ["pyserial==3.1.1"],
        'bluetooth': ["pybluez"],
        'lxml': ["lxml"],
    },
    entry_points={
        'console_scripts': [
            'openxc-dashboard = openxc.tools.dashboard:main',
            'openxc-dump = openxc.tools.dump:main',
            'openxc-control = openxc.tools.control:main',
            'openxc-gps = openxc.tools.gps:main',
            'openxc-trace-split = openxc.tools.tracesplit:main',
            'openxc-generate-firmware-code = openxc.tools.generate_code:main',
            'openxc-diag = openxc.tools.diagnostics:main',
            'openxc-scanner = openxc.tools.scanner:main',
            'openxc-obd2scanner = openxc.tools.obd2scanner:main',
        ]
    },
)
