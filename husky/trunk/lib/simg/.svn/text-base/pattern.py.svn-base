#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

"""
See <Singleton> design pattern for detail: http://www.oodesign.com/singleton-pattern.html
Python <Singleton> reference: http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
Recommend use Singleton as a metaclass
"""


def singleton(cls):
    """
    Method: decorator
    While objects created using MyClass() would be true singleton objects, 
    MyClass itself is a a function, not a class, so you cannot call class methods from it. 
    Also for m = MyClass(); n = MyClass(); o = type(n)(); then m == n && m != o && n != o
    """
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance


class Singleton(type):
    """
    Method: metaclass
    """
    _instances = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
    
    pass