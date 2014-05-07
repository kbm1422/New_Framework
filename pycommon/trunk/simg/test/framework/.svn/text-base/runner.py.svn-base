#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import time
import uuid
import threading

from .result import TestResult
from .context import TestContextManager
from .resource import TestResourcePool


class TestRunner(threading.Thread):
    def __init__(self, uid=None, result=None, failfast=False, reskey=None, ctxattrs={}):
        self.uid = uid
        name = str(self.uid) if self.uid else str(uuid.uuid1())
        threading.Thread.__init__(self, name=name)

        self.failfast = failfast
        self.result = result or TestResult()
        self.reskey = reskey
        self.__ctxattrs = ctxattrs
        self.__suites = []
        self.context = None

    def addSuite(self, suite):
        self.__suites.append(suite)

    def run(self):
        """
        1. acquire TestResource object from TestResourcePool
        2. while acquiring the resource, if self.result.shouldStop is True, stop acquiring the resource, and then exit the run (for web control purpose)
        3. if acquired the resource, assign it to context and then run all suites.
        4. after finishing all suites, release the resource and remove the context.
        """
        ctxmgr = TestContextManager()
        respool = TestResourcePool()

        reskey = None
        resobj = None
        while True:
            try:
                reskey, resobj = respool.acquire(self.reskey, block=False)
                break
            except KeyError:
                time.sleep(0.5)
            finally:
                if self.result.shouldStop:
                    if resobj:
                        respool.release(reskey, resobj)
                    return

        self.context = ctxmgr.newCurrentContext()
        self.context.resource = resobj
        for key, value in self.__ctxattrs.items():
            setattr(self.context, key, value)
        try:
            resobj.doActionBeforeTestRun()
            for suite in self.__suites:
                suite.run(self.result)
        except KeyboardInterrupt:
            logger.warn("KeyboardInterrupt")
            self.stop()
            self.join()
        except:
            logger.exception("")
            raise
        finally:
            resobj.doActionAfterTestRun()
            respool.release(reskey, resobj)
            ctxmgr.delCurrentContext()

    def pause(self):
        self.result.pause()

    def resume(self):
        self.result.resume()

    def stop(self):
        self.result.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
