#!/usr/bin/python
# -*- coding: utf-8 -*-


import logging
logger = logging.getLogger(__name__)

import time
import threading
import collections
from abc import ABCMeta
from simg.pattern import Singleton


class TestResource(object):
    __metaclass__ = ABCMeta

    def doActionBeforeTestRun(self):
        pass

    def doActionBeforeTest(self, test):
        pass

    def doActionAfterTest(self, test):
        pass

    def doActionAfterTestRun(self):
        pass


class FullError(Exception):
    pass


class TestResourcePool(object):
    """
    See <ObjectPool> design pattern for detail: http://www.oodesign.com/object-pool-pattern.html
    """
    __metaclass__ = Singleton

    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self.__odict = collections.OrderedDict()
        self.__conditions = {}
        self.__delevents = {}
        self.__mutex_odict = threading.RLock()

    def put(self, key, obj, block=True, timeout=None):
        with self.__mutex_odict:
            if key in self.__odict:
                del self.__odict[key]
                self.__conditions.pop(key).notify_all()
            self._put(key, obj, block, timeout)

    def remove(self, key, block=True, timeout=None):
        """
        1. check whether item(key, obj) is in self._odict,
            a) if exists, remove it and return
            b) if not exists, goto step2
        2. check whether key is in self._conditions:
            a) if exists, it means the item(key, obj) is using and not released. do following steps:
                1) create a delete event, put it into self._delevents
                2) waiting this event consumed and set by self._put method
                    i  ) if block is not True, raise KeyError
                    ii ) if timeout is not None, if time out is reached, raise KeyError
                    iii) if block is True and timeout is None, waiting until the event has been set and return
            b) if not exists, it means item has already been removed, raise KeyError
        """
        with self.__mutex_odict:
            if key in self.__odict:
                del self.__odict[key]
                self.__conditions.pop(key).notify_all()
                return

        if key in self.__conditions:
            if key not in self.__delevents:
                self.__delevents[key] = threading.Event()
            event = self.__delevents[key]
            if not block:
                if not event.is_set():
                    raise KeyError
            elif timeout is None:
                while not event.is_set():
                    event.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time.time() + timeout
                while not event.is_set():
                    remaining = endtime - time.time()
                    if remaining <= 0.0:
                        raise KeyError
                    event.wait(remaining)
        else:
            raise KeyError

    def acquire(self, key=None, block=True, timeout=None):
        if key is None:
            return self._pop(block, timeout)
        else:
            return self._get(key, block, timeout)

    def release(self, key, obj, block=True, timeout=None):
        with self.__mutex_odict:
            if key not in self.__odict:
                self._put(key, obj, block, timeout)

    def size(self):
        with self.__mutex_odict:
            n = len(self.__odict)
            return n

    def is_empty(self):
        return not self.size()

    def is_full(self):
        return 0 < self.maxsize == self.size()

    def _pop(self, last=False, block=True, timeout=None):
        if not block:
            with self.__mutex_odict:
                if not len(self.__odict):
                    raise KeyError
                else:
                    key, obj = self.__odict.popitem(last)
                    return key, obj
        else:
            if timeout:
                starttime = time.time()

            while True:
                self.__mutex_odict.acquire()
                try:
                    if not len(self.__odict):
                        time.sleep(0.1)
                        continue
                    else:
                        key, obj = self.__odict.popitem(last)
                        return key, obj

                    if timeout and time.time() - starttime > timeout:
                            raise KeyError
                finally:
                    self.__mutex_odict.release()

    def _get(self, key, block=True, timeout=None):
        condition = self.__conditions[key]
        condition.acquire()
        try:
            if not block:
                if key not in self.__odict:
                    raise KeyError
            elif timeout is None:
                while key not in self.__odict and key in self.__conditions:
                    condition.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time.time() + timeout
                while key not in self.__odict and key in self.__conditions:
                    remaining = endtime - time.time()
                    if remaining <= 0.0:
                        raise KeyError
                    condition.wait(remaining)

            obj = self.__odict.pop(key)
            return key, obj
        finally:
            condition.release()

    def _put(self, key, obj, block=True, timeout=None):
        """
        1. check whether the item(key, obj) should be removed
        2. if it should be removed:
            a) don't put back to self._odict
            b) notify all threads which are waiting for the item, these threads raise KeyError because the item is not exists
            c) pop the event from the self._delevents and then set it, so the self.remove method will get the event
        """
        if key in self.__delevents:
            self.__conditions.pop(key).notify_all()
            self.__delevents.pop(key).set()
        else:
            if key not in self.__conditions:
                self.__conditions[key] = threading.Condition(self.__mutex_odict)

            condition = self.__conditions[key]
            condition.acquire()
            try:
                if self.maxsize > 0:
                    if not block:
                        if self.size() == self.maxsize:
                            raise FullError
                    elif timeout is None:
                        while self.size() == self.maxsize:
                            condition.wait()
                    elif timeout < 0:
                        raise ValueError("'timeout' must be a non-negative number")
                    else:
                        endtime = time.time() + timeout
                        while self.size() == self.maxsize:
                            remaining = endtime - time.time()
                            if remaining <= 0.0:
                                raise FullError
                            condition.wait(remaining)
                self.__odict[key] = obj
                condition.notify()
            finally:
                condition.release()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s %(thread)-5d [%(levelname)-8s] - %(message)s'
    )
