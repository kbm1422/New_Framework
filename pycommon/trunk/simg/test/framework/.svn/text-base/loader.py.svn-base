#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import pprint
import importlib
from collections import OrderedDict

from simg.test.framework import LinkedTestCase
from simg.test.framework import TestSuite, LinkedTestSuite


class TestLoader(object):

    @staticmethod
    def _validateDataType(data):
        if not isinstance(data, dict) or isinstance(data, OrderedDict):
            raise TypeError

    def loadTestCaseFromDict(self, data):
        """
        @param data:
        TestCase:
        {"class":"", "caseid": 123, "name": "", "methodName": test_XX, }

        LinkedTestCase:
        {"class":"", "caseid": 123, "name": "", "methodNames": ["test_1", "test_2"]}
        {"class":"", "caseid": 123, "name": ""}
        """
        self._validateDataType(data)
        logger.info("loadTestCaseFromDict: \n%s", pprint.pformat(data))

        clsname = data.pop("class")
        parts = clsname.split('.')
        modname = ".".join(parts[:-1])
        module = importlib.import_module(modname)
        cls = getattr(module, parts[-1])

        if cls is LinkedTestCase or issubclass(cls, LinkedTestCase):
            methodNames = data.pop("methodNames", None)
            case = cls(methodNames)
        else:
            methodName = data.pop("methodName")
            case = cls(methodName)

        for name, value in data.items():
            if hasattr(case, name):
                setattr(case, name, value)
            else:
                raise AttributeError("case '%s' has no attribute '%s'" % (case, name))
        return case

    def loadTestSuiteFromDict(self, data):
        """
        @param data:
        {
        "type": 1,
        "name": ""
        "tests": [
                  {"class":"", "method": None },
                  {"type":"", "name": "", "suiteid": 123, "tests": [] }
                 ]
        }
        """
        self._validateDataType(data)
        logger.info("loadTestSuiteFromDict: \n%s", pprint.pformat(data))

        stype = data.pop("type")
        if stype == 1:
            suite = TestSuite()
        elif stype == 2:
            suite = LinkedTestSuite()
        else:
            raise ValueError

        for subdata in data.pop("tests"):
            if "class" in subdata:
                case = self.loadTestCaseFromDict(subdata)
                suite.addTest(case)
            else:
                subsuite = self.loadTestSuiteFromDict(subdata)
                suite.addTest(subsuite)

        for name, value in data.items():
            if hasattr(suite, name):
                setattr(suite, name, value)
            else:
                raise AttributeError("suite '%s' has no attribute '%s'" % (suite, name))

        return suite


if __name__ == "__main__":
    pass
