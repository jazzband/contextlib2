#!/usr/bin/env python
from distutils.core import setup

# Technically, unittest2 is a dependency to run the tests on 2.7
# This file ignores that, since I don't want to depend on
# setuptools just to get "tests_require" support

setup(
    name='contextlib2',
    version=open('VERSION.txt').read().strip(),
    py_modules=['contextlib2'],
    license='PSF License',
    description='Backports and enhancements for the contextlib module',
    long_description=open('README.rst').read(),
    author='Nick Coghlan',
    author_email='ncoghlan@gmail.com',
    url='http://contextlib2.readthedocs.org',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Python Software Foundation License',
        # These are the Python versions tested, it may work on others
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

)