#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import unittest
import shelve
from abc import ABCMeta, abstractmethod


class TestResult(unittest.TestResult):
    def __init__(self, *args, **kwargs):
        unittest.TestResult.__init__(self, *args, **kwargs)
        self.successes = []
        self.warnings = []
        self.caseRecords = []
        self.suiteRecords = []
        self.shouldPause = False
        self.__handlers = []

    def addHandler(self, handler):
        self.__handlers.append(handler)

    def removeHandler(self, handler):
        self.__handlers.remove(handler)

    def callHandlers(self, record):
        for handler in self.__handlers:
            handler.emit(record)

    def addTestCaseResultRecord(self, record):
        self.caseRecords.append(record)
        self.callHandlers(record)

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
        if test.record.warnings:
            status = test.record.WARNING
            self.warnings.append(test)
        else:
            status = test.record.PASSED
            self.successes.append(test)
        test.record.status = status
        self.addTestCaseResultRecord(test.record)

    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        if hasattr(test, "exc_info_to_string"):
            error = self._formatError(err, test, relevant=False)
            test.record.status = test.record.ERRONEOUS
            test.record.error = error
            self.addTestCaseResultRecord(test.record)
        else:
            logger.error(self._exc_info_to_string(err, test))

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        error = self._formatError(err, test, relevant=True)
        test.record.status = test.record.FAILED
        test.record.error = error
        self.addTestCaseResultRecord(test.record)

    def addSkip(self, test, reason):
        unittest.TestResult.addSkip(self, test, reason)
        test.record.status = test.record.SKIPPED
        test.record.skipreason = reason
        self.addTestCaseResultRecord(test.record)

    def addExpectedFailure(self, test, err):
        unittest.TestResult.addExpectedFailure(self, test, err)
        error = self._formatError(err, test, relevant=False)
        test.record.status = test.record.PASSED
        test.record.error = error
        self.addTestCaseResultRecord(test.record)

    def addUnexpectedSuccess(self, test):
        unittest.TestResult.addUnexpectedSuccess(self, test)
        test.record.status = test.record.FAILED
        self.addTestCaseResultRecord(test.record)

    def _formatError(self, exc_info, test, relevant):
        error = (exc_info[0], exc_info[1], test.exc_info_to_string(exc_info, relevant))
        logger.error(error[2])
        return error

    def pause(self):
        self.shouldPause = True

    def resume(self):
        self.shouldPause = False


class BaseRecordHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def emit(self, record):
        """a hook method, will be called in TestResult.callHandlers"""
        pass


class ShelveRecordHandler(BaseRecordHandler):
    def __init__(self, filename):
        self._filename = filename
        shd = shelve.open(self._filename)
        if not "records" in shd:
            shd["records"] = []
        shd.close()

    def emit(self, record):
        shd = shelve.open(self._filename, protocol=2, writeback=True)
        shd["records"].append(record)
        shd.close()


class HttpRecordHandler(BaseRecordHandler):
    def __init__(self, url):
        self._http = None

    def emit(self, record):
        raise NotImplementedError


class RecordHandlerFactory(object):
    """
    See <Factory> design pattern for detail: http://www.oodesign.com/factory-pattern.html
    """
    @classmethod
    def newRecordHandler(cls, **kwargs):
        if "filename" in kwargs:
            hdlrclass = ShelveRecordHandler
        elif "url" in kwargs:
            hdlrclass = HttpRecordHandler
        else:
            raise ValueError
        return hdlrclass(**kwargs)


if __name__ == "__main__":
    pass
