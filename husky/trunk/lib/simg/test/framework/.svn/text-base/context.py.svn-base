#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import sys
import time
import threading
from simg.pattern import Singleton


class TestContext(object):
    """
    TestContext is a thread local object which used to transmit the data between TestRunner, TestSuite and TestCase.
    """
    def __init__(self):
        self.bindir = os.path.dirname(sys.executable) if hasattr(sys, '_MEIPASS') else sys.path[0]
        self.logdir = os.path.join(os.path.dirname(self.bindir), "logs", time.strftime("%Y-%m-%d_%H-%M-%S"))
        self.logfmt = "%(asctime)-15s - %(thread)-5d [%(levelname)-8s] - %(message)s"
        self.logfrn = "simg"  # filter record name, used to generate log in TestSuite
        self.resource = None  # should be set by TestRunner
        self.curtsuite = None  # indicate current running TestSuite, would be used by TestCase. It should be set by TestSuite.


class TestContextManager(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.__contexts = {}
        self.__mutex = threading.RLock()
        self.__defaultContext = None

    def newContext(self, name):
        context = TestContext()
        with self.__mutex:
            self.__contexts[name] = context
        return context

    def newCurrentContext(self):
        thread = threading.current_thread()
        return self.newContext(thread.name)

    def __getDefaultContext(self):
        if self.__defaultContext is None:
            self.__defaultContext = TestContext()
        return self.__defaultContext

    def getCurrentContext(self):
        thread = threading.current_thread()
        with self.__mutex:
            context = self.__contexts.get(thread.name, self.__getDefaultContext())
        return context

    def delCurrentContext(self):
        thread = threading.current_thread()
        self.delContext(thread.name)

    def delContext(self, name):
        with self.__mutex:
            del self.__contexts[name]


if __name__ == "__main__":
    pass
