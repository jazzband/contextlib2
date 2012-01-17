Release History
---------------

0.3.1 (2012-01-17)
~~~~~~~~~~~~~~~~~~

* Issue #7: Add MANIFEST.in so PyPI package contains all relevant files

0.3 (2012-01-04)
~~~~~~~~~~~~~~~~

* Issue #5: ContextStack.register no longer pointlessly returns the wrapped
  function
* Issue #2: Add examples and recipes section to docs
* Issue #3: ContextStack.register_exit() now accepts objects with __exit__
  attributes in addition to accepting exit callbacks directly
* Issue #1: Add ContextStack.preserve() to move all registered callbacks to
  a new ContextStack object
* Wrapped callbacks now expose __wrapped__ (for direct callbacks) or __self__
  (for context manager methods) attributes to aid in introspection
* Moved version number to a VERSION.txt file (read by both docs and setup.py)
* Added NEWS.rst (and incorporated into documentation)


0.2 (2011-12-15)
~~~~~~~~~~~~~~~~

* Renamed CleanupManager to ContextStack (hopefully before anyone started
  using the module for anything, since I didn't alias the old name at all)


0.1 (2011-12-13)
~~~~~~~~~~~~~~~~

* Initial release as a backport module
* Added CleanupManager (based on a `Python feature request`_)
* Added ContextDecorator.refresh_cm() (based on a `Python tracker issue`_)
  
.. _Python feature request: http://bugs.python.org/issue13585
.. _Python tracker issue: http://bugs.python.org/issue11647
