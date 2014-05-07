#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from abc import ABCMeta

from simg.pattern import Singleton


class AVConsumerFactory(object):
    __metaclass__ = Singleton
    @classmethod
    def newAVProducer(cls, **kwargs):
        pass


class AbstractAVConsumer(object):
    __metaclass__ = ABCMeta


class TV(AbstractAVConsumer):
    pass
