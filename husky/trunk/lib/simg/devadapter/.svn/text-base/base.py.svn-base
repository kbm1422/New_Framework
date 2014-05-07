#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from abc import ABCMeta, abstractmethod
from collections import namedtuple

VendorMsg = namedtuple('VendorMsg', ["vendorID", "dstMacAddr", "length", "data"])
Wvan = namedtuple('Wvan', ["name", "id", "hr", "lr"])


class DevAdapterError(Exception):
    pass


class DevAdapterCmdError(DevAdapterError):
    pass


class BaseDevAdapter(object):
    __metaclass__ = ABCMeta

    class DeviceType(object):
        SRC = 0
        SINK = 1

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def sendcmd(self, cmd, timeout, interval, trim):
        pass

    @abstractmethod
    def connect(self, dstMacAddr):
        """
        SWAM3:  connect_device 0
        DRIVER: echo mac_addr > /sys/devices/virtual/video/sii6400/wihd/connect
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        SWAM3:  disconnect_device
        DRIVER: echo 0 > /sys/devices/virtual/video/sii6400/wihd/connect
        """
        pass

    @abstractmethod
    def getFwVersion(self):
        """
        SWAM3:  show_version
        DRIVER: cat /sys/devices/virtual/video/sii6400/fw_version
        """
        pass

    @abstractmethod
    def getFwBuild(self):
        pass

    @abstractmethod
    def getDevState(self):
        """
        SWAM3:  dev_get_state
        DRIVER: cat /sys/devices/virtual/video/sii6400/wihd/remote_device/signal_strength
        """
        pass

    @abstractmethod
    def getLinkQuality(self):
        """
        SWAM3:  get_hr_link_quality
        DRIVER: cat /sys/devices/virtual/video/sii6400/wihd/remote_device/signal_strength
        """
        pass

    @abstractmethod
    def setMacAddress(self, macaddr):
        """
        SWAM3:  custparamset 0 XX:XX:XX:XX:XX:XX
        DRIVER: echo XXXXXXXXXXXX /sys/devices/virtual/video/sii6400/wihd/self/mac_addr
        """
        pass

    @abstractmethod
    def getMacAddress(self):
        """
        SWAM3:  custparamget 0
        DRIVER: cat /sys/devices/virtual/video/sii6400/wihd/self/mac_addr
        """
        pass

    @abstractmethod
    def setDeviceName(self, name):
        """
        SWAM3:  custparamset 2 DeviceName
        DRIVER: echo name > /sys/devices/virtual/video/sii6400/wihd/self/name
        """
        pass

    @abstractmethod
    def getDeviceName(self):
        """
        SWAM3:  custparamget 2
        DRIVER: cat > /sys/devices/virtual/video/sii6400/wihd/self/name
        """
        pass

    @abstractmethod
    def upgradeFirmware(self, filename):
        pass

    @abstractmethod
    def setVendorMsgFilter(self, msgFilter):
        """
        0x0: None.  Block all vendor messages [default]
        3 bytes: Organizationally Unique Identfier (OUI) assigned to the vendor by IEEE
        0xFFFFFF: All. Allow all vendor messages to be received
        """
        pass

    @abstractmethod
    def sendVendorMsg(self, msg):
        """
        VendorMsg = namedtuple('VendorMsg', ["vendorID", "dstMacAddr", "length", "data"])
        vendorID :  3-byte vendor ID.  Must be an Organizationally Unique Identfier (OUI) assigned to the vendor by IEEE
        dstMacAddr: 6-byte destination MAC address in hexadecimal with octets separated by ‘:’.  For broadcast messages, use FF:FF:FF:FF:FF:FF
        length:     Length of the message data in bytes (0-16)
        data:       0-16 bytes of message data to transmit.  Format is hexadecimal with 0x prefix and bytes separated by spaces (for example, 0x11 0x22 0x33)
        """
        pass


if __name__ == "__main__":
    pass
