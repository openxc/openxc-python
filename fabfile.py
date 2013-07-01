
"""
@file    openxc-python\fabfile.py Fab File Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4
"""

from __future__ import with_statement

import os
from fabric.api import abort, local, task, lcd, puts


@task(default=True)
def docs(clean='no', browse_='no'):
    """Docs Routine
    @param clean specifies if the clean should be processed.  The default
    setting is 'no'.
    @param browse_ specifies if the docs should be processed with browse
    to include the source code.  The default setting is 'no'."""
    with lcd('docs'):
        local('make clean html')
    temp_path = "/tmp/openxc-python-docs"
    docs_path = "%s/docs/_build/html" % local("pwd", capture=True)
    local('rm -rf %s' % temp_path)
    os.makedirs(temp_path)
    with lcd(temp_path):
        local('cp -R %s %s' % (docs_path, temp_path))
    local('git checkout gh-pages')
    local('cp -R %s/html/* .' % temp_path)
    local('touch .nojekyll')
    local('git add -A')
    local('git commit -m "Update Sphinx docs."')
    local('git push')
    local('git checkout master')


@task
def browse():
    """
    Open the current dev docs in a browser tab.
    """
    local("$BROWSER docs/_build/html/index.html")


@task(default=True)
def test(args=None):
    """Test Task Routine
    @param args the args input parameter."""
    local("tox")


@task
def upload():
    """
    Build, register and upload to PyPI
    """
    puts("Uploading to PyPI")
    local('python setup.py sdist register upload')
