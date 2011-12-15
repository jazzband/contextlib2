.. contextlib2 documentation master file, created by
   sphinx-quickstart on Tue Dec 13 20:29:56 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

contextlib2 --- Updated utilities for with-statement contexts
=============================================================

.. module:: contextlib2
   :synopsis: Backports and future enhancements for the contextlib module

This module provides backports of features in the latest version of the
standard library's :mod:`contextlib` module to earlier Python versions. It
also serves as a real world proving ground for potential future enhancements
to that module.

Like :mod:`contextlib`, this module provides utilities for common tasks
involving the ``with`` statement.


Additions Relative to the Standard Library
------------------------------------------

This module is primarily a backport of the Python 3.2 version of
:mod:`contextlib` to earlier releases. However, it is also a proving ground
for new features not yet part of the standard library. Those new features
are currently:

* :meth:`ContextDecorator.refresh_cm`
* :class:`CleanupManager`


API Reference
-------------

.. function:: @contextmanager

   This function is a decorator that can be used to define a factory
   function for ``with`` statement context managers, without needing to
   create a class or separate :meth:`__enter__` and :meth:`__exit__` methods.

   A simple example (this is not recommended as a real way of generating HTML!)::

      from contextlib import contextmanager

      @contextmanager
      def tag(name):
          print("<%s>" % name)
          yield
          print("</%s>" % name)

      >>> with tag("h1"):
      ...    print("foo")
      ...
      <h1>
      foo
      </h1>

   The function being decorated must return a generator-iterator when
   called. This iterator must yield exactly one value, which will be bound to
   the targets in the ``with`` statement's ``as`` clause, if any.

   At the point where the generator yields, the block nested in the ``with``
   statement is executed.  The generator is then resumed after the block is exited.
   If an unhandled exception occurs in the block, it is reraised inside the
   generator at the point where the yield occurred.  Thus, you can use a
   ``try``...\ ``except``...\ ``finally`` statement to trap
   the error (if any), or ensure that some cleanup takes place. If an exception is
   trapped merely in order to log it or to perform some action (rather than to
   suppress it entirely), the generator must reraise that exception. Otherwise the
   generator context manager will indicate to the ``with`` statement that
   the exception has been handled, and execution will resume with the statement
   immediately following the ``with`` statement.

   :func:`contextmanager` uses :class:`ContextDecorator` so the context managers
   it creates can be used as decorators as well as in ``with`` statements.
   When used as a decorator, a new generator instance is implicitly created on
   each function call (this allows the otherwise "one-shot" context managers
   created by :func:`contextmanager` to meet the requirement that context
   managers support multiple invocations in order to be used as decorators).


.. function:: closing(thing)

   Return a context manager that closes *thing* upon completion of the block.  This
   is basically equivalent to::

      from contextlib import contextmanager

      @contextmanager
      def closing(thing):
          try:
              yield thing
          finally:
              thing.close()

   And lets you write code like this::

      from contextlib import closing
      from urllib.request import urlopen

      with closing(urlopen('http://www.python.org')) as page:
          for line in page:
              print(line)

   without needing to explicitly close ``page``.  Even if an error occurs,
   ``page.close()`` will be called when the ``with`` block is exited.


.. class:: ContextDecorator()

   A base class that enables a context manager to also be used as a decorator.

   Context managers inheriting from ``ContextDecorator`` have to implement
   :meth:`__enter__` and :meth:`__exit__` as normal. :meth:`__exit__` retains its optional
   exception handling even when used as a decorator.

   ``ContextDecorator`` is used by :func:`contextmanager`, so you get this
   functionality automatically.

   Example of ``ContextDecorator``::

      from contextlib import ContextDecorator

      class mycontext(ContextDecorator):
          def __enter__(self):
              print('Starting')
              return self

          def __exit__(self, *exc):
              print('Finishing')
              return False

      >>> @mycontext()
      ... def function():
      ...     print('The bit in the middle')
      ...
      >>> function()
      Starting
      The bit in the middle
      Finishing

      >>> with mycontext():
      ...     print('The bit in the middle')
      ...
      Starting
      The bit in the middle
      Finishing

   This change is just syntactic sugar for any construct of the following form::

      def f():
          with cm():
              # Do stuff

   ``ContextDecorator`` lets you instead write::

      @cm()
      def f():
          # Do stuff

   It makes it clear that the ``cm`` applies to the whole function, rather than
   just a piece of it (and saving an indentation level is nice, too).

   Existing context managers that already have a base class can be extended by
   using ``ContextDecorator`` as a mixin class::

      from contextlib import ContextDecorator

      class mycontext(ContextBaseClass, ContextDecorator):
          def __enter__(self):
              return self

          def __exit__(self, *exc):
              return False

   .. method:: refresh_cm()

      This method is invoked each time a call is made to a decorated function.
      The default implementation just returns *self*.

      As the decorated function must be able to be called multiple times, the
      underlying context manager must normally support use in multiple
      ``with`` statements (preferably in a thread-safe manner). If
      this is not the case, then the context manager must define this method
      and return a *new* copy of the context manager on each invocation.

      This may involve keeping a copy of the original arguments used to
      first initialise the context manager.


.. class:: ContextStack()

   A context manager that is designed to make it easy to programmatically
   combine other context managers and cleanup functions, especially those
   that are optional or otherwise driven by input data.

   For example, a set of files may easily be handled in a single with
   statement as follows::

      with ContextStack() as stack:
          files = [stack.enter_context(fname) for fname in filenames]
          # All opened files will automatically be closed at the end of
          # the with statement, even if attempts to open files later
          # in the list throw an exception

   Each instance maintains a stack of registered callbacks (usually context
   manager exit methods) that are called in reverse order when the instance
   is closed (either explicitly or implicitly at the end of a ``with``
   statement).

   Since registered callbacks are invoked in the reverse order of
   registration, this ends up behaving as if multiple nested ``with``
   statements had been used with the registered set of resources. This even
   extends to exception handling - if an inner callback suppresses or replaces
   an exception, then outer callbacks will be passed arguments based on that
   that updated state.

   .. method:: enter_context(cm):

      Enters a new context manager and adds its :meth:`__exit__` method to
      the callback stack. The return value is the result of the context
      manager's own :meth:`__enter__` method.

      These context managers may suppress exceptions just as they normally
      would if used directly as part of a ``with`` statement.

   .. method:: register_exit(callback):

      Directly accepts a callback with the same signature as a
      context manager's :meth:`__exit__` method and adds it to the callback
      stack.

      By returning true values, these callbacks can suppress exceptions the
      same way context manager :meth:`__exit__` methods can.

   .. method:: push_callback(callback, *args, **kwds):

      Accepts an arbitrary callback function and arguments and adds it to
      the callback stack.

      Unlike the other methods, callbacks added this way cannot suppress
      exceptions (as they are never passed the exception details).

   .. method:: close()

      Immediately unwinds the context stack, invoking callbacks in the
      reverse order of registration. For any context managers and exit
      callbacks registered, the arguments passed in will indicate that no
      exception occurred.


Obtaining the Module
====================

This module can be installed directly from the `Python Package Index`_ with
pip_::

    pip install contextlib2

Alternatively, you can download and unpack it manually from the `contextlib2
PyPI page`_.

There are no operating system or distribution specific versions of this
module - it is a pure Python module that should work on all platforms.

Supported Python versions are currently 2.7 and 3.2+.

.. _Python Package Index: http://pypi.python.org
.. _pip: http://www.pip-installer.org
.. _contextlib2 pypi page: http://pypi.python.org/pypi/contextlib2


Development and Support
-----------------------

contextlib2 is developed and maintained on BitBucket_. Problems and suggested
improvements can be posted to the `issue tracker`_.

.. _BitBucket: https://bitbucket.org/ncoghlan/contextlib2/overview
.. _issue tracker: https://bitbucket.org/ncoghlan/contextlib2/issues?status=new&status=open


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

