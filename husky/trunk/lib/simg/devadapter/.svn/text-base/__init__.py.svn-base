#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

import sys

from .base import VendorMsg
from .driver import LocalDriverAdapter, SSHDriverAdapter
from .swam3 import LocalSWAM3Adapter, SWAM3Connection, SWAM3Server
from simg.pattern import Singleton


class DevAdapterFactory(object):
    __metaclass__ = Singleton
    """
    See <Factory> design pattern for detail: http://www.oodesign.com/factory-pattern.html
    """
    @classmethod
    def newDevAdapter(cls, **kwargs):
        """
        new DevAdapter object according to kwargs
        @param: kwargs:
                SSHDriverAdapter: adb, devpath
                LocalDriverAdapter: adb, host, port=22, username=None, password=None, devpath="/sys/devices/virtual/video/sii6400"
                SWAM3Connection: addr
                LocalSWAM3Adapter: moduleid, portno, logfilename, ap_moduleid=None
        """
        devcls = None
        if "host" in kwargs:
            devcls = SSHDriverAdapter
        elif "addr" in kwargs:
            devcls = SWAM3Connection    # Fixme: should specify GEN3Connection or BAConnection
        else:
            if sys.platform.startswith("linux"):
                devcls = LocalDriverAdapter
            else:
                devcls = LocalSWAM3Adapter
        return devcls(**kwargs)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
