#!/usr/bin/env python
from distutils.core import setup

setup(
    name='contextlib2',
    version=open('VERSION.txt').read().strip(),
    py_modules=['contextlib2'],
    license='PSF License',
    description='Backports and enhancements for the contextlib module',
    long_description=open('README.txt').read(),
    author='Nick Coghlan',
    author_email='ncoghlan@gmail.com',
    url='http://contextlib2.readthedocs.org'
)
