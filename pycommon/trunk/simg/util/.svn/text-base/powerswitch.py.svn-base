#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

import time
import urllib2
import base64
from abc import ABCMeta
from HTMLParser import HTMLParser

from simg.pattern import Singleton


class SwitchOutletError(Exception):
    pass


class PowerSwitchOutletFactory(object):
    __metaclass__ = Singleton
    @classmethod
    def newPowerSwitchOutlet(cls, **kwargs):
        if kwargs:
            logger.debug("kwargs is not empty, create a PowerSwitchOutlet")
            return PowerSwitchOutlet(**kwargs)
        else:
            logger.debug("kwargs is empty, create a NullPowerSwitchOutlet")
            return NullPowerSwitchOutlet()


class BasePowerSwitchOutlet(object):
    __metaclass__ = ABCMeta

    def turnon(self):
        pass

    def turnoff(self):
        pass

    def cycle(self, interval=0.0):
        pass


class NullPowerSwitchOutlet(BasePowerSwitchOutlet):
    """
    See <Null Object> design pattern for detail: http://www.oodesign.com/null-object-pattern.html
    """


class PowerSwitchOutlet(BasePowerSwitchOutlet):
    def __init__(self, host, outlet, username="admin", password="sqa"):
        self._powswitch = PowerSwitchController(host, username, password)
        self._outlet = outlet

    def turnon(self):
        self._powswitch.turnon(self._outlet)
    
    def turnoff(self):
        self._powswitch.turnoff(self._outlet)

    def cycle(self, interval=1.0):
        self._powswitch.cycle(self._outlet, interval)

    def getStatus(self):
        self._powswitch.getStatus(self._outlet)

   

class PowerSwitchController(object):
    def __init__(self, host, username="admin", password="1234"):
        self.host = host
        self.username = username
        self.password = password

    def _request(self, url):
        """ Get a URL from the userid/password protected powerswitch page, return None on failure"""
        request = urllib2.Request("http://%s%s" % (self.host, url))
        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)   
        try:
            result = urllib2.urlopen(request).read()
        except urllib2.URLError:
            return None
        return result
    
    def turnoff(self, outlet):
        logger.info("request power switch outlet %s OFF", outlet)
        self._request('/outlet?%s=OFF' % outlet)
        if self.getStatus(outlet) != "OFF":
            raise SwitchOutletError
    
    def turnon(self, outlet):
        logger.info("request power switch outlet %s ON", outlet)
        self._request('/outlet?%s=ON' % outlet)
        if self.getStatus(outlet) != "ON":
            raise SwitchOutletError

    def cycle(self, outlet, interval=1.0):
        if self.getStatus(outlet) != "OFF":
            self.turnoff(outlet)
            time.sleep(interval)
            self.turnon(outlet)

    def getStatus(self, outlet):
        allstatus = self.getAllStatus()
        return allstatus[int(outlet) - 1]

    def getAllStatus(self):
        states = []
        resp = self._request("/index.htm")

        class Parser(HTMLParser):
            def handle_data(self, data):
                if data == "ON" or data == "OFF":
                    states.append(data)
        parser = Parser()
        try:
            parser.feed(resp)
        finally:
            parser.close()
        logger.debug("power switch all outlets status: %s", states)
        return states


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
    null = NullPowerSwitchOutlet()
    null.turnon()
