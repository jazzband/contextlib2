Release History
---------------


0.3 (2012-01-XX)
~~~~~~~~~~~~~~~~

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
