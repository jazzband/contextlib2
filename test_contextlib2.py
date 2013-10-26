#!/usr/bin/env python
"""Unit tests for contextlib2"""

import io
import sys

# Check for a sufficiently recent unittest module
import unittest
if not hasattr(unittest, "skipIf"):
    import unittest2 as unittest

# Handle 2/3 compatibility for redirect_stdout testing,
# checking 3.x only implicit exception chaining behaviour
# and checking for exception details in test cases
if str is bytes:
    # Python 2
    from io import BytesIO as StrIO
    check_exception_chaining = False

    def check_exception_details(case, exc_type, regex):
        return case.assertRaisesRegexp(exc_type, regex)
else:
    # Python 3
    from io import StringIO as StrIO
    check_exception_chaining = True

    def check_exception_details(case, exc_type, regex):
        return case.assertRaisesRegex(exc_type, regex)


from contextlib2 import *  # Tests __all__

class ContextManagerTestCase(unittest.TestCase):

    def test_instance_docstring_given_function_docstring(self):
        # Issue 19330: ensure context manager instances have good docstrings
        # See http://bugs.python.org/issue19404 for why this doesn't currently
        # affect help() output :(
        def gen_with_docstring():
            """This has a docstring"""
            yield
        gen_docstring = gen_with_docstring.__doc__
        cm_with_docstring = contextmanager(gen_with_docstring)
        self.assertEqual(cm_with_docstring.__doc__, gen_docstring)
        obj = cm_with_docstring()
        self.assertEqual(obj.__doc__, gen_docstring)
        self.assertNotEqual(obj.__doc__, type(obj).__doc__)

    def test_contextmanager_plain(self):
        state = []
        @contextmanager
        def woohoo():
            state.append(1)
            yield 42
            state.append(999)
        with woohoo() as x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
        self.assertEqual(state, [1, 42, 999])

    def test_contextmanager_finally(self):
        state = []
        @contextmanager
        def woohoo():
            state.append(1)
            try:
                yield 42
            finally:
                state.append(999)
        with self.assertRaises(ZeroDivisionError):
            with woohoo() as x:
                self.assertEqual(state, [1])
                self.assertEqual(x, 42)
                state.append(x)
                raise ZeroDivisionError()
        self.assertEqual(state, [1, 42, 999])

    def test_contextmanager_no_reraise(self):
        @contextmanager
        def whee():
            yield
        ctx = whee()
        ctx.__enter__()
        # Calling __exit__ should not result in an exception
        self.assertFalse(ctx.__exit__(TypeError, TypeError("foo"), None))

    def test_contextmanager_trap_yield_after_throw(self):
        @contextmanager
        def whoo():
            try:
                yield
            except:
                yield
        ctx = whoo()
        ctx.__enter__()
        self.assertRaises(
            RuntimeError, ctx.__exit__, TypeError, TypeError("foo"), None
        )

    def test_contextmanager_except(self):
        state = []
        @contextmanager
        def woohoo():
            state.append(1)
            try:
                yield 42
            except ZeroDivisionError as e:
                state.append(e.args[0])
                self.assertEqual(state, [1, 42, 999])
        with woohoo() as x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
            raise ZeroDivisionError(999)
        self.assertEqual(state, [1, 42, 999])

    def _create_contextmanager_attribs(self):
        def attribs(**kw):
            def decorate(func):
                for k,v in kw.items():
                    setattr(func,k,v)
                return func
            return decorate
        @contextmanager
        @attribs(foo='bar')
        def baz(spam):
            """Whee!"""
        return baz

    def test_contextmanager_attribs(self):
        baz = self._create_contextmanager_attribs()
        self.assertEqual(baz.__name__,'baz')
        self.assertEqual(baz.foo, 'bar')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    def test_contextmanager_doc_attrib(self):
        baz = self._create_contextmanager_attribs()
        self.assertEqual(baz.__doc__, "Whee!")

class ClosingTestCase(unittest.TestCase):

    def test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = closing.__doc__
        obj = closing(None)
        self.assertEqual(obj.__doc__, cm_docstring)

    def test_closing(self):
        state = []
        class C:
            def close(self):
                state.append(1)
        x = C()
        self.assertEqual(state, [])
        with closing(x) as y:
            self.assertEqual(x, y)
        self.assertEqual(state, [1])

    def test_closing_error(self):
        state = []
        class C:
            def close(self):
                state.append(1)
        x = C()
        self.assertEqual(state, [])
        with self.assertRaises(ZeroDivisionError):
            with closing(x) as y:
                self.assertEqual(x, y)
                1 / 0
        self.assertEqual(state, [1])


class mycontext(ContextDecorator):
    """Example decoration-compatible context manager for testing"""
    started = False
    exc = None
    catch = False

    def __enter__(self):
        self.started = True
        return self

    def __exit__(self, *exc):
        self.exc = exc
        return self.catch


class TestContextDecorator(unittest.TestCase):

    def test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = mycontext.__doc__
        obj = mycontext()
        self.assertEqual(obj.__doc__, cm_docstring)

    def test_contextdecorator(self):
        context = mycontext()
        with context as result:
            self.assertIs(result, context)
            self.assertTrue(context.started)

        self.assertEqual(context.exc, (None, None, None))


    def test_contextdecorator_with_exception(self):
        context = mycontext()

        with check_exception_details(self, NameError, 'foo'):
            with context:
                raise NameError('foo')
        self.assertIsNotNone(context.exc)
        self.assertIs(context.exc[0], NameError)

        context = mycontext()
        context.catch = True
        with context:
            raise NameError('foo')
        self.assertIsNotNone(context.exc)
        self.assertIs(context.exc[0], NameError)


    def test_decorator(self):
        context = mycontext()

        @context
        def test():
            self.assertIsNone(context.exc)
            self.assertTrue(context.started)
        test()
        self.assertEqual(context.exc, (None, None, None))


    def test_decorator_with_exception(self):
        context = mycontext()

        @context
        def test():
            self.assertIsNone(context.exc)
            self.assertTrue(context.started)
            raise NameError('foo')

        with check_exception_details(self, NameError, 'foo'):
            test()
        self.assertIsNotNone(context.exc)
        self.assertIs(context.exc[0], NameError)


    def test_decorating_method(self):
        context = mycontext()

        class Test(object):

            @context
            def method(self, a, b, c=None):
                self.a = a
                self.b = b
                self.c = c

        # these tests are for argument passing when used as a decorator
        test = Test()
        test.method(1, 2)
        self.assertEqual(test.a, 1)
        self.assertEqual(test.b, 2)
        self.assertEqual(test.c, None)

        test = Test()
        test.method('a', 'b', 'c')
        self.assertEqual(test.a, 'a')
        self.assertEqual(test.b, 'b')
        self.assertEqual(test.c, 'c')

        test = Test()
        test.method(a=1, b=2)
        self.assertEqual(test.a, 1)
        self.assertEqual(test.b, 2)


    def test_typo_enter(self):
        class mycontext(ContextDecorator):
            def __unter__(self):
                pass
            def __exit__(self, *exc):
                pass

        with self.assertRaises(AttributeError):
            with mycontext():
                pass


    def test_typo_exit(self):
        class mycontext(ContextDecorator):
            def __enter__(self):
                pass
            def __uxit__(self, *exc):
                pass

        with self.assertRaises(AttributeError):
            with mycontext():
                pass


    def test_contextdecorator_as_mixin(self):
        class somecontext(object):
            started = False
            exc = None

            def __enter__(self):
                self.started = True
                return self

            def __exit__(self, *exc):
                self.exc = exc

        class mycontext(somecontext, ContextDecorator):
            pass

        context = mycontext()
        @context
        def test():
            self.assertIsNone(context.exc)
            self.assertTrue(context.started)
        test()
        self.assertEqual(context.exc, (None, None, None))


    def test_contextmanager_as_decorator(self):
        @contextmanager
        def woohoo(y):
            state.append(y)
            yield
            state.append(999)

        state = []
        @woohoo(1)
        def test(x):
            self.assertEqual(state, [1])
            state.append(x)
        test('something')
        self.assertEqual(state, [1, 'something', 999])

        # Issue #11647: Ensure the decorated function is 'reusable'
        state = []
        test('something else')
        self.assertEqual(state, [1, 'something else', 999])


class TestExitStack(unittest.TestCase):

    def test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = ExitStack.__doc__
        obj = ExitStack()
        self.assertEqual(obj.__doc__, cm_docstring)

    def test_no_resources(self):
        with ExitStack():
            pass

    def test_callback(self):
        expected = [
            ((), {}),
            ((1,), {}),
            ((1,2), {}),
            ((), dict(example=1)),
            ((1,), dict(example=1)),
            ((1,2), dict(example=1)),
        ]
        result = []
        def _exit(*args, **kwds):
            """Test metadata propagation"""
            result.append((args, kwds))
        with ExitStack() as stack:
            for args, kwds in reversed(expected):
                if args and kwds:
                    f = stack.callback(_exit, *args, **kwds)
                elif args:
                    f = stack.callback(_exit, *args)
                elif kwds:
                    f = stack.callback(_exit, **kwds)
                else:
                    f = stack.callback(_exit)
                self.assertIs(f, _exit)
            for wrapper in stack._exit_callbacks:
                self.assertIs(wrapper.__wrapped__, _exit)
                self.assertNotEqual(wrapper.__name__, _exit.__name__)
                self.assertIsNone(wrapper.__doc__, _exit.__doc__)
        self.assertEqual(result, expected)

    def test_push(self):
        exc_raised = ZeroDivisionError
        def _expect_exc(exc_type, exc, exc_tb):
            self.assertIs(exc_type, exc_raised)
        def _suppress_exc(*exc_details):
            return True
        def _expect_ok(exc_type, exc, exc_tb):
            self.assertIsNone(exc_type)
            self.assertIsNone(exc)
            self.assertIsNone(exc_tb)
        class ExitCM(object):
            def __init__(self, check_exc):
                self.check_exc = check_exc
            def __enter__(self):
                self.fail("Should not be called!")
            def __exit__(self, *exc_details):
                self.check_exc(*exc_details)
        with ExitStack() as stack:
            stack.push(_expect_ok)
            self.assertIs(stack._exit_callbacks[-1], _expect_ok)
            cm = ExitCM(_expect_ok)
            stack.push(cm)
            self.assertIs(stack._exit_callbacks[-1].__self__, cm)
            stack.push(_suppress_exc)
            self.assertIs(stack._exit_callbacks[-1], _suppress_exc)
            cm = ExitCM(_expect_exc)
            stack.push(cm)
            self.assertIs(stack._exit_callbacks[-1].__self__, cm)
            stack.push(_expect_exc)
            self.assertIs(stack._exit_callbacks[-1], _expect_exc)
            stack.push(_expect_exc)
            self.assertIs(stack._exit_callbacks[-1], _expect_exc)
            1/0

    def test_enter_context(self):
        class TestCM(object):
            def __enter__(self):
                result.append(1)
            def __exit__(self, *exc_details):
                result.append(3)

        result = []
        cm = TestCM()
        with ExitStack() as stack:
            @stack.callback  # Registered first => cleaned up last
            def _exit():
                result.append(4)
            self.assertIsNotNone(_exit)
            stack.enter_context(cm)
            self.assertIs(stack._exit_callbacks[-1].__self__, cm)
            result.append(2)
        self.assertEqual(result, [1, 2, 3, 4])

    def test_close(self):
        result = []
        with ExitStack() as stack:
            @stack.callback
            def _exit():
                result.append(1)
            self.assertIsNotNone(_exit)
            stack.close()
            result.append(2)
        self.assertEqual(result, [1, 2])

    def test_pop_all(self):
        result = []
        with ExitStack() as stack:
            @stack.callback
            def _exit():
                result.append(3)
            self.assertIsNotNone(_exit)
            new_stack = stack.pop_all()
            result.append(1)
        result.append(2)
        new_stack.close()
        self.assertEqual(result, [1, 2, 3])

    def test_exit_raise(self):
        with self.assertRaises(ZeroDivisionError):
            with ExitStack() as stack:
                stack.push(lambda *exc: False)
                1/0

    def test_exit_suppress(self):
        with ExitStack() as stack:
            stack.push(lambda *exc: True)
            1/0

    def test_exit_exception_chaining_reference(self):
        # Sanity check to make sure that ExitStack chaining matches
        # actual nested with statements
        # We still run this under Py2, but the only thing it actually
        # checks in that case is that the outermost exception is IndexError
        # and that the inner ValueError was suppressed
        class RaiseExc(object):
            def __init__(self, exc):
                self.exc = exc
            def __enter__(self):
                return self
            def __exit__(self, *exc_details):
                raise self.exc

        class RaiseExcWithContext(object):
            def __init__(self, outer, inner):
                self.outer = outer
                self.inner = inner
            def __enter__(self):
                return self
            def __exit__(self, *exc_details):
                try:
                    raise self.inner
                except:
                    raise self.outer

        class SuppressExc(object):
            def __enter__(self):
                return self
            def __exit__(self, *exc_details):
                type(self).saved_details = exc_details
                return True

        try:
            with RaiseExc(IndexError):
                with RaiseExcWithContext(KeyError, AttributeError):
                    with SuppressExc():
                        with RaiseExc(ValueError):
                            1 / 0
        except IndexError as exc:
            if check_exception_chaining:
                self.assertIsInstance(exc.__context__, KeyError)
                self.assertIsInstance(exc.__context__.__context__, AttributeError)
                # Inner exceptions were suppressed
                self.assertIsNone(exc.__context__.__context__.__context__)
        else:
            self.fail("Expected IndexError, but no exception was raised")
        # Check the inner exceptions
        inner_exc = SuppressExc.saved_details[1]
        self.assertIsInstance(inner_exc, ValueError)
        if check_exception_chaining:
            self.assertIsInstance(inner_exc.__context__, ZeroDivisionError)

    def test_exit_exception_chaining(self):
        # Ensure exception chaining matches the reference behaviour
        # We still run this under Py2, but the only thing it actually
        # checks in that case is that the outermost exception is IndexError
        # and that the inner ValueError was suppressed
        def raise_exc(exc):
            raise exc

        saved_details = []
        def suppress_exc(*exc_details):
            saved_details[:] = [exc_details]
            return True

        try:
            with ExitStack() as stack:
                stack.callback(raise_exc, IndexError)
                stack.callback(raise_exc, KeyError)
                stack.callback(raise_exc, AttributeError)
                stack.push(suppress_exc)
                stack.callback(raise_exc, ValueError)
                1 / 0
        except IndexError as exc:
            if check_exception_chaining:
                self.assertIsInstance(exc.__context__, KeyError)
                self.assertIsInstance(exc.__context__.__context__, AttributeError)
                # Inner exceptions were suppressed
                self.assertIsNone(exc.__context__.__context__.__context__)
        else:
            self.fail("Expected IndexError, but no exception was raised")
        # Check the inner exceptions
        inner_exc = saved_details[0][1]
        self.assertIsInstance(inner_exc, ValueError)
        if check_exception_chaining:
            self.assertIsInstance(inner_exc.__context__, ZeroDivisionError)

    def test_exit_exception_non_suppressing(self):
        # http://bugs.python.org/issue19092
        def raise_exc(exc):
            raise exc

        def suppress_exc(*exc_details):
            return True

        try:
            with ExitStack() as stack:
                stack.callback(lambda: None)
                stack.callback(raise_exc, IndexError)
        except Exception as exc:
            self.assertIsInstance(exc, IndexError)
        else:
            self.fail("Expected IndexError, but no exception was raised")

        try:
            with ExitStack() as stack:
                stack.callback(raise_exc, KeyError)
                stack.push(suppress_exc)
                stack.callback(raise_exc, IndexError)
        except Exception as exc:
            self.assertIsInstance(exc, KeyError)
        else:
            self.fail("Expected KeyError, but no exception was raised")

    def test_body_exception_suppress(self):
        def suppress_exc(*exc_details):
            return True
        try:
            with ExitStack() as stack:
                stack.push(suppress_exc)
                1/0
        except IndexError as exc:
            self.fail("Expected no exception, got IndexError")

    def test_exit_exception_chaining_suppress(self):
        with ExitStack() as stack:
            stack.push(lambda *exc: True)
            stack.push(lambda *exc: 1/0)
            stack.push(lambda *exc: {}[1])

    def test_excessive_nesting(self):
        # The original implementation would die with RecursionError here
        with ExitStack() as stack:
            for i in range(10000):
                stack.callback(int)

    def test_instance_bypass(self):
        class Example(object): pass
        cm = Example()
        cm.__exit__ = object()
        stack = ExitStack()
        self.assertRaises(AttributeError, stack.enter_context, cm)
        stack.push(cm)
        self.assertIs(stack._exit_callbacks[-1], cm)

class TestRedirectStdout(unittest.TestCase):

    def test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = redirect_stdout.__doc__
        obj = redirect_stdout(None)
        self.assertEqual(obj.__doc__, cm_docstring)

    def test_redirect_to_string_io(self):
        f = StrIO()
        msg = "Consider an API like help(), which prints directly to stdout"
        with redirect_stdout(f):
            print(msg)
        s = f.getvalue().strip()
        self.assertEqual(s, msg)

    def test_enter_result_is_target(self):
        f = StrIO()
        with redirect_stdout(f) as enter_result:
            self.assertIs(enter_result, f)

    def test_cm_is_reusable(self):
        f = StrIO()
        write_to_f = redirect_stdout(f)
        with write_to_f:
            print("Hello")
        with write_to_f:
            print("World!")
        s = f.getvalue()
        self.assertEqual(s, "Hello\nWorld!\n")

    # If this is ever made reentrant, update the reusable-but-not-reentrant
    # example at the end of the contextlib docs accordingly.
    def test_nested_reentry_fails(self):
        f = StrIO()
        write_to_f = redirect_stdout(f)
        with check_exception_details(self, RuntimeError, "Cannot reenter"):
            with write_to_f:
                print("Hello")
                with write_to_f:
                    print("World!")


class TestSuppress(unittest.TestCase):

    def test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = suppress.__doc__
        obj = suppress()
        self.assertEqual(obj.__doc__, cm_docstring)

    def test_no_result_from_enter(self):
        with suppress(ValueError) as enter_result:
            self.assertIsNone(enter_result)

    def test_no_exception(self):
        with suppress(ValueError):
            self.assertEqual(pow(2, 5), 32)

    def test_exact_exception(self):
        with suppress(TypeError):
            len(5)

    def test_exception_hierarchy(self):
        with suppress(LookupError):
            'Hello'[50]

    def test_other_exception(self):
        with self.assertRaises(ZeroDivisionError):
            with suppress(TypeError):
                1/0

    def test_no_args(self):
        with self.assertRaises(ZeroDivisionError):
            with suppress():
                1/0

    def test_multiple_exception_args(self):
        with suppress(ZeroDivisionError, TypeError):
            1/0
        with suppress(ZeroDivisionError, TypeError):
            len(5)

    def test_cm_is_reentrant(self):
        ignore_exceptions = suppress(Exception)
        with ignore_exceptions:
            pass
        with ignore_exceptions:
            len(5)
        with ignore_exceptions:
            1/0
            with ignore_exceptions: # Check nested usage
                len(5)

class TestContextStack(unittest.TestCase):

    def test_no_resources(self):
        with ContextStack():
            pass

    def test_register(self):
        expected = [
            ((), {}),
            ((1,), {}),
            ((1,2), {}),
            ((), dict(example=1)),
            ((1,), dict(example=1)),
            ((1,2), dict(example=1)),
        ]
        result = []
        def _exit(*args, **kwds):
            """Test metadata propagation"""
            result.append((args, kwds))
        with ContextStack() as stack:
            for args, kwds in reversed(expected):
                if args and kwds:
                    f = stack.register(_exit, *args, **kwds)
                elif args:
                    f = stack.register(_exit, *args)
                elif kwds:
                    f = stack.register(_exit, **kwds)
                else:
                    f = stack.register(_exit)
                self.assertIs(f, _exit)
            for wrapper in stack._exit_callbacks:
                self.assertIs(wrapper.__wrapped__, _exit)
                self.assertNotEqual(wrapper.__name__, _exit.__name__)
                self.assertIsNone(wrapper.__doc__, _exit.__doc__)
        self.assertEqual(result, expected)

    def test_register_exit(self):
        exc_raised = ZeroDivisionError
        def _expect_exc(exc_type, exc, exc_tb):
            self.assertIs(exc_type, exc_raised)
        def _suppress_exc(*exc_details):
            return True
        def _expect_ok(exc_type, exc, exc_tb):
            self.assertIsNone(exc_type)
            self.assertIsNone(exc)
            self.assertIsNone(exc_tb)
        class ExitCM(object):
            def __init__(self, check_exc):
                self.check_exc = check_exc
            def __enter__(self):
                self.fail("Should not be called!")
            def __exit__(self, *exc_details):
                self.check_exc(*exc_details)
        with ContextStack() as stack:
            stack.register_exit(_expect_ok)
            self.assertIs(stack._exit_callbacks[-1], _expect_ok)
            cm = ExitCM(_expect_ok)
            stack.register_exit(cm)
            self.assertIs(stack._exit_callbacks[-1].__self__, cm)
            stack.register_exit(_suppress_exc)
            self.assertIs(stack._exit_callbacks[-1], _suppress_exc)
            cm = ExitCM(_expect_exc)
            stack.register_exit(cm)
            self.assertIs(stack._exit_callbacks[-1].__self__, cm)
            stack.register_exit(_expect_exc)
            self.assertIs(stack._exit_callbacks[-1], _expect_exc)
            stack.register_exit(_expect_exc)
            self.assertIs(stack._exit_callbacks[-1], _expect_exc)
            1/0

    def test_enter_context(self):
        class TestCM(object):
            def __enter__(self):
                result.append(1)
            def __exit__(self, *exc_details):
                result.append(3)

        result = []
        cm = TestCM()
        with ContextStack() as stack:
            @stack.register  # Registered first => cleaned up last
            def _exit():
                result.append(4)
            self.assertIsNotNone(_exit)
            stack.enter_context(cm)
            self.assertIs(stack._exit_callbacks[-1].__self__, cm)
            result.append(2)
        self.assertEqual(result, [1, 2, 3, 4])

    def test_close(self):
        result = []
        with ContextStack() as stack:
            @stack.register
            def _exit():
                result.append(1)
            self.assertIsNotNone(_exit)
            stack.close()
            result.append(2)
        self.assertEqual(result, [1, 2])

    def test_preserve(self):
        result = []
        with ContextStack() as stack:
            @stack.register
            def _exit():
                result.append(3)
            self.assertIsNotNone(_exit)
            new_stack = stack.preserve()
            result.append(1)
        result.append(2)
        new_stack.close()
        self.assertEqual(result, [1, 2, 3])

    def test_instance_bypass(self):
        class Example(object): pass
        cm = Example()
        cm.__exit__ = object()
        stack = ContextStack()
        self.assertRaises(AttributeError, stack.enter_context, cm)
        stack.register_exit(cm)
        self.assertIs(stack._exit_callbacks[-1], cm)

if __name__ == "__main__":
    unittest.main()
