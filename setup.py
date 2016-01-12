#!/usr/bin/env python
from distutils.core import setup

# Technically, unittest2 is a dependency to run the tests on 2.6 and 3.1
# This file ignores that, since I don't want to depend on distribute
# or setuptools just to get "tests_require" support

setup(
    name='contextlib2',
    version=open('VERSION.txt').read().strip(),
    py_modules=['contextlib2'],
    license='PSF License',
    description='Backports and enhancements for the contextlib module',
    long_description=open('README.md').read(),
    author='Nick Coghlan',
    author_email='ncoghlan@gmail.com',
    url='http://contextlib2.readthedocs.org'
)
