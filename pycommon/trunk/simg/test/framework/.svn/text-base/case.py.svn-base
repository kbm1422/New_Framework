#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import sys
import inspect
import collections

import traceback
import unittest

from .result import TestResult


class TestCaseResultRecord(object):
    PASSED = 1
    WARNING = 2
    FAILED = 3
    SKIPPED = 4
    ERRONEOUS = 5

    def __init__(self):
        self.caseid = None
        self.testid = None
        self.name = None
        self.status = None
        self.error = None
        self.skipreason = None
        self.warnings = []
        self.checkpoints = []
        self.concerns = collections.OrderedDict()
        self.timecost = None  # will be set by TestSuite

    def __repr__(self):
        return "<TestCaseResultRecord '%s(ID:%s, STATUS:%s)'>" % (self.name, self.testid, self.status)

    def __str__(self):
        return self.__repr__()


class TestCase(unittest.TestCase):
    """
    @summary:
    All assert methods support an additional param "iswarning".
    When failureException is occurred and iswarning is True, it will be captured and then be saved as an warningException into self.warnings.
    It is useful when some check point does not affect the overall test result.

    Method self.addConcern used to add concern into an OrderedDict when test is running.
    You can use this method to collect the data you are pay attention to.
    """

    warningException = Warning
    longMessage = True

    def __init__(self, methodName="runTest", caseid=None, testid=None, name=None):
        unittest.TestCase.__init__(self, methodName)
        self.record = TestCaseResultRecord()
        self.caseid = caseid
        self.testid = testid
        self.name = name
        if self.name is None:
            if isLinkedTestCase(self):
                self.name = self.__class__.__name__
            else:
                self.name = self._testMethodName

        self.record = TestCaseResultRecord()
        self.record.caseid = self.caseid
        self.record.testid = self.testid
        self.record.name = self.name

        # below attribute will be set by TestSuite
        self.logdir = None
        self.logname = None
        self.cycleindex = None

        # below attribute will be set by TestResource
        self.extlognames = []

    def defaultTestResult(self):
        return TestResult()

    def addConcern(self, name, value):
        self.record.concerns[name] = value

    def warn(self, msg):
        try:
            raise self.warningException(msg)
        except self.warningException:
            exc_info = sys.exc_info()
            warning = (exc_info[0], exc_info[1], self.exc_info_to_string(exc_info))
            logger.warn(warning[2])
            self.record.warnings.append(warning)

    def exc_info_to_string(self, exc_info, relevant=True):
        pre_stacktraces = traceback.extract_stack()
        cur_stacetraces = traceback.extract_tb(exc_info[2])
        full_stacktraces = pre_stacktraces[:-1] + cur_stacetraces

        stacktraces = []
        if relevant:
            title = "Traceback (relevant call)"
            for stacktrace in full_stacktraces:
                if stacktrace[3].startswith("self.assert"):
                    stacktraces.append(stacktrace)
        else:
            title = "Traceback (most recent call last)"
            stacktraces = full_stacktraces

        exc_line = traceback.format_exception_only(exc_info[0], exc_info[1])
        return "%s:\n%s%s" % (title, "".join(traceback.format_list(stacktraces)), "".join(exc_line))

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if name.startswith("assert") and inspect.ismethod(attr):
            print name
            def wrapper(*args, **kwargs):
                """
                See <decorator> design pattern for detail: http://www.oodesign.com/decorator-pattern.html
                """
                argspec = inspect.getargspec(attr)
                # argspec[0]: ['self', 'first', 'second', 'msg']
                # args: (1, 2, 'test equal', True
                if len(args) == len(argspec[0]):
                    iswarning = args[-1]
                    args = args[:-1]
                else:
                    iswarning = kwargs.pop("iswarning", False)

                status = None
                try:
                    attr(*args, **kwargs)
                except self.failureException:
                    if iswarning:
                        status = TestCaseResultRecord.WARNING
                        exc_info = sys.exc_info()
                        warning = (self.warningException, exc_info[1], self.exc_info_to_string((self.warningException, exc_info[1], exc_info[2])))
                        logger.warn(warning[2])
                        self.record.warnings.append(warning)
                    else:
                        status = TestCaseResultRecord.FAILED
                        raise
                else:
                    status = TestCaseResultRecord.PASSED
                finally:
                    try:
                        params = inspect.getcallargs(attr, *args, **kwargs)
                    except AttributeError as err:
                        #handle jython error
                        logger.error("%s, can't collect the checkpoint from param 'msg'", str(err))
                    else:
                        if "msg" in params:
                            self.record.checkpoints.append((params["msg"], status))
            return wrapper
        else:
            return attr


class LinkedTestCase(TestCase):
    """
    @summary:
    LinkedTestCase means there are several test methods will be run in this case.
    Each failed 'assert' will cause the whole case failed, the following test methods in this case will not be executed.
    This is useful when the later test method depends on the previous test method's result
    """
    methodNames = ()

    def __init__(self, methodNames=()):
        self._linkedMethodNames = methodNames or self.methodNames
        if not (isinstance(self._linkedMethodNames, tuple) or isinstance(self._linkedMethodNames, list)):
            raise TypeError

        if not self._linkedMethodNames:
            raise
        TestCase.__init__(self, "runLinkedTests")

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self._linkedMethodNames == other._linkedMethodNames

    def __hash__(self):
        return hash((type(self), self._linkedMethodNames))

    def runLinkedTests(self):
        for methodName in self._linkedMethodNames:
            methodFunc = getattr(self, methodName)
            methodFunc()


def isTestCase(test):
    return isinstance(test, TestCase) or issubclass(test.__class__, TestCase)


def isLinkedTestCase(test):
    return isinstance(test, LinkedTestCase) or issubclass(test.__class__, LinkedTestCase)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
