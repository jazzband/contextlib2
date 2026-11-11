#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Note: The minimum Python version requirement is set on the basis of
#       "if it's not tested, it's broken".
#       Specifically, if a Python version is no longer available for testing
#       in CI, then the minimum supported Python version will be increased.
#       That way there's no risk of a release that breaks older Python versions.

setup(
    name='contextlib2',
    version=open('VERSION.txt').read().strip(),
    python_requires='>=3.7',
    packages=['contextlib2'],
    include_package_data=True,
    license='PSF License',
    description='Backports and enhancements for the contextlib module',
    long_description=open('README.rst').read(),
    author='Alyssa Coghlan',
    author_email='ncoghlan@gmail.com',
    url='https://github.com/jazzband/contextlib2',
    project_urls= {
        'Documentation': 'https://contextlib2.readthedocs.org',
        'Source': 'https://github.com/jazzband/contextlib2.git',
        'Issue Tracker': 'https://github.com/jazzband/contextlib2.git',
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'License :: OSI Approved :: Python Software Foundation License',
        # These are the Python versions tested, it may work on others
        # It definitely won't work on versions without native async support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],

)
