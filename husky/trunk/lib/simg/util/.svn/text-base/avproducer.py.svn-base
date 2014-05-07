#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from abc import ABCMeta

from simg.pattern import Singleton


class AVProducerFactory(object):
    __metaclass__ = Singleton
    @classmethod
    def newAVProducer(cls, **kwargs):
        pass


class AbstractAVProducer(object):
    __metaclass__ = ABCMeta


class BDP(AbstractAVProducer):
    pass


class QD(AbstractAVProducer):
    pass


class Astro8700(AbstractAVProducer):
    pass