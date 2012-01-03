.. contextlib2 documentation master file, created by
   sphinx-quickstart on Tue Dec 13 20:29:56 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

contextlib2 --- Updated utilities for context management
========================================================

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

* :class:`ContextStack`
* :meth:`ContextDecorator.refresh_cm`


API Reference
=============

.. function:: contextmanager

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

   .. versionchanged:: 0.1
      Made the standard library's private :meth:`refresh_cm` API public


.. class:: ContextStack()

   A context manager that is designed to make it easy to programmatically
   combine other context managers and cleanup functions, especially those
   that are optional or otherwise driven by input data.

   For example, a set of files may easily be handled in a single with
   statement as follows::

      with ContextStack() as stack:
          files = [stack.enter_context(open(fname)) for fname in filenames]
          # All opened files will automatically be closed at the end of
          # the with statement, even if attempts to open files later
          # in the list throw an exception

   Each instance maintains a stack of registered callbacks that are called in
   reverse order when the instance is closed (either explicitly or implicitly
   at the end of a ``with`` statement). Note that callbacks are *not* invoked
   implicitly when the context stack instance is garbage collected.

   Since registered callbacks are invoked in the reverse order of
   registration, this ends up behaving as if multiple nested ``with``
   statements had been used with the registered set of callbacks. This even
   extends to exception handling - if an inner callback suppresses or replaces
   an exception, then outer callbacks will be passed arguments based on that
   updated state.

   .. method:: enter_context(cm)

      Enters a new context manager and adds its :meth:`__exit__` method to
      the callback stack. The return value is the result of the context
      manager's own :meth:`__enter__` method.

      These context managers may suppress exceptions just as they normally
      would if used directly as part of a ``with`` statement.

   .. method:: register_exit(callback)

      Directly accepts a callback with the same signature as a
      context manager's :meth:`__exit__` method and adds it to the callback
      stack.

      By returning true values, these callbacks can suppress exceptions the
      same way context manager :meth:`__exit__` methods can.

      This method also accepts any object with an ``__exit__`` method, and
      will register that method as the callback. This is mainly useful to
      cover part of an :meth:`__enter__` implementation with a context
      manager's own :meth:`__exit__` method.

   .. method:: register(callback, *args, **kwds)

      Accepts an arbitrary callback function and arguments and adds it to
      the callback stack.

      Unlike the other methods, callbacks added this way cannot suppress
      exceptions (as they are never passed the exception details).

   .. method:: preserve()

      Transfers the callback stack to a fresh instance and returns it. No
      callbacks are invoked by this operation - instead, they will now be
      invoked when the new stack is closed (either explicitly or implicitly).

      For example, a group of files can be opened as an "all or nothing"
      operation as follows::

         with ContextStack() as stack:
             files = [stack.enter_context(open(fname)) for fname in filenames]
             close_files = stack.preserve().close
             # If opening any file fails, all previously opened files will be
             # closed automatically. If all files are opened successfully,
             # they will remain open even after the with statement ends.
             # close_files() can then be invoked explicitly to close them all

      .. versionadded:: 0.3

   .. method:: close()

      Immediately unwinds the callback stack, invoking callbacks in the
      reverse order of registration. For any context managers and exit
      callbacks registered, the arguments passed in will indicate that no
      exception occurred.

   .. versionadded:: 0.2
      New API for :mod:`contextlib2`, not available in standard library


Examples and Recipes
====================

This section describes some examples and recipes for making effective use of
the tools provided by :mod:`contextlib2`. Some of them may also work with
:mod:`contextlib` in sufficiently recent versions of Python. When this is the
case, it is noted at the end of the example.


Using a context manager as a function decorator
-----------------------------------------------

:class:`ContextDecorator` makes it possible to use a context manager in
both an ordinary ``with`` statement and also as a function decorator. The
:meth:`ContextDecorator.refresh_cm` method even makes it possible to use
otherwise single use context managers (such as those created by
:func:`contextmanager`) that way.

For example, it is sometimes useful to wrap functions or groups of statements
with a logger that can track the time of entry and time of exit.  Rather than
writing both a function decorator and a context manager for the task,
:func:`contextmanager` provides both capabilities in a single
definition::

    from contextlib2 import contextmanager
    import logging

    logging.basicConfig(level=logging.INFO)

    @contextmanager
    def track_entry_and_exit(name):
        logging.info('Entering: {}'.format(name))
        yield
        logging.info('Exiting: {}'.format(name))

This can be used as both a context manager::

    with track_entry_and_exit('widget loader'):
        print('Some time consuming activity goes here')
        load_widget()

And also as a function decorator::

    @track_entry_and_exit('widget loader')
    def activity():
        print('Some time consuming activity goes here')
        load_widget()

Note that there is one additional limitation when using context managers
as function decorators: there's no way to access the return value of
:meth:`__enter__`. If that value is needed, then it is still necessary to use
an explicit ``with`` statement.

This example should also work with :mod:`contextlib` in Python 3.2.1 or later.


Cleaning up in an ``__enter__`` implementation
----------------------------------------------

As noted in the documentation of :meth:`ContextStack.register_exit`, this
method can be useful in cleaning up an already allocated resource if later
steps in the :meth:`__enter__` implementation fail.

Here's an example of doing this for a context manager that accepts resource
acquisition and release functions, along with an optional validation function,
and maps them to the context management protocol::

   from contextlib2 import ContextStack

   class ResourceManager(object):

       def __init__(self, acquire_resource, release_resource, check_resource_ok=None):
           self.acquire_resource = acquire_resource
           self.release_resource = release_resource
           self.check_resource_ok = check_resource_ok

       def __enter__(self):
           resource = self.acquire_resource()
           if self.check_resource_ok is not None:
               with ContextStack() as stack:
                   stack.register_exit(self)
                   if not self.check_resource_ok(resource):
                       msg = "Failed validation for {!r}"
                       raise RuntimeError(msg.format(resource))
                   # The validation check passed and didn't raise an exception
                   # Accordingly, we want to keep the resource, and pass it
                   # back to our caller
                   stack.preserve()
           return resource

       def __exit__(self, *exc_details):
           # We don't need to duplicate any of our resource release logic
           self.release_resource()


Replacing any use of ``try-finally`` and flag variables
-------------------------------------------------------

A pattern you will sometimes see is a ``try-finally`` statement with a flag
variable to indicate whether or not the body of the ``finally`` clause should
be executed. In its simplest form (that can't already be handled just by
using an ``except`` clause instead), it looks something like this::

   cleanup_needed = True
   try:
       result = perform_operation()
       if result:
           cleanup_needed = False
   finally:
       if cleanup_needed:
           cleanup_resources()

As with any ``try`` statement based code, this can cause problems for
development and review, because the setup code and the cleanup code can end
up being separated by arbitrarily long sections of code.

:class:`ContextStack` makes it possible to instead register a callback for
execution at the end of a ``with`` statement, and then later decide to skip
executing that callback::

   from contextlib2 import ContextStack

   with ContextStack() as stack:
       stack.register(cleanup_resources)
       result = perform_operation()
       if result:
           stack.preserve()

This allows the intended cleanup up behaviour to be made explicit up front,
rather than requiring a separate flag variable.

If you find yourself using this pattern a lot, it can be simplified even
further by means of a small helper class::

   from contextlib2 import ContextStack

   class Callback(ContextStack):
       def __init__(self, callback, *args, **kwds):
           super(Callback, self).__init__()
           self.register(callback, *args, **kwds)

       def cancel(self):
           self.preserve()

   with Callback(cleanup_resources) as cb:
       result = perform_operation()
       if result:
           cb.cancel()

If the resource cleanup isn't already neatly bundled into a standalone
function, then it is still possible to use the decorator form of
:meth:`ContextStack.register_exit` to declare the resource cleanup in
advance::

   from contextlib2 import ContextStack

   with ContextStack() as stack:
       @stack.register_exit
       def cleanup_resources(*exc_details):
           ...
       result = perform_operation()
       if result:
           stack.preserve()


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


.. include:: ../NEWS.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
