#!/usr/bin/env python
"""Unit tests for contextlib.py, and other context managers."""

import sys
import unittest

from contextlib2 import *  # Tests __all__


class ContextManagerTestCase(unittest.TestCase):

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

    # XXX This needs more work

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

    def test_contextdecorator(self):
        context = mycontext()
        with context as result:
            self.assertIs(result, context)
            self.assertTrue(context.started)

        self.assertEqual(context.exc, (None, None, None))


    def test_contextdecorator_with_exception(self):
        context = mycontext()

        with self.assertRaises(NameError):
            with context:
                raise NameError('foo')
        self.assertIsNotNone(context.exc)
        self.assertIs(context.exc[0], NameError)
        self.assertIn('foo', str(context.exc[1]))

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

        with self.assertRaises(NameError):
            test()
        self.assertIsNotNone(context.exc)
        self.assertIs(context.exc[0], NameError)
        self.assertIn('foo', str(context.exc[1]))


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
                    self.assertIsNone(stack.register(_exit, *args, **kwds))
                elif args:
                    self.assertIsNone(stack.register(_exit, *args))
                elif kwds:
                    self.assertIsNone(stack.register(_exit, **kwds))
                else:
                    self.assertIsNone(stack.register(_exit))
            for wrapper in stack._callbacks:
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
            self.assertIs(stack._callbacks[-1], _expect_ok)
            cm = ExitCM(_expect_ok)
            stack.register_exit(cm)
            self.assertIs(stack._callbacks[-1].__self__, cm)
            stack.register_exit(_suppress_exc)
            self.assertIs(stack._callbacks[-1], _suppress_exc)
            cm = ExitCM(_expect_exc)
            stack.register_exit(cm)
            self.assertIs(stack._callbacks[-1].__self__, cm)
            stack.register_exit(_expect_exc)
            self.assertIs(stack._callbacks[-1], _expect_exc)
            stack.register_exit(_expect_exc)
            self.assertIs(stack._callbacks[-1], _expect_exc)
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
            stack.enter_context(cm)
            self.assertIs(stack._callbacks[-1].__self__, cm)
            result.append(2)
        self.assertEqual(result, [1, 2, 3, 4])

    def test_close(self):
        result = []
        with ContextStack() as stack:
            @stack.register
            def _exit():
                result.append(1)
            stack.close()
            result.append(2)
        self.assertEqual(result, [1, 2])

    def test_preserve(self):
        result = []
        with ContextStack() as stack:
            @stack.register
            def _exit():
                result.append(3)
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
        self.assertIs(stack._callbacks[-1], cm)
        
if __name__ == "__main__":
    import unittest
    unittest.main(__name__)
