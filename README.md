contextlib2 is a backport of the [standard library's contextlib
module](https://docs.python.org/3.5/library/contextlib.html) to
earlier Python versions.

It also serves as a real world proving ground for possible future
enhancements to the standard library version.

Development
-----------

contextlib2 currently has no dependencies.

Local testing is currently just a matter of running `python test_contextlib2.py`.

You can test against multiple versions of Python with [tox](http://tox.testrun.org/)):

    pip install tox
    tox

Versions currently tested in tox are:

* CPython 2.7 (also tested in Codeship)
* CPython 3.4 (also tested in Codeship)
* CPython 3.5
* PyPy
* PyPy3

To install all the relevant runtimes on Fedora 23:

    sudo dnf install python python3 pypy pypy3
    sudo dnf copr enable -y mstuchli/Python3.5
    sudo dnf install python35-python3

Continuous integration
----------------------

CI is set up in Codeship to run against PRs and commits.

[![Codeship Status for ncoghlan/contextlib2](https://codeship.com/projects/884e9500-3d1a-0133-3eb0-1abe7f570a4c/status?branch=default)](https://codeship.com/projects/102388)
[![codecov.io](https://codecov.io/bitbucket/ncoghlan/contextlib2/coverage.svg?branch=default)](https://codecov.io/bitbucket/ncoghlan/contextlib2?branch=default)
