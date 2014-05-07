#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import re
import time
import subprocess
import simg.net.ssh

from abc import ABCMeta, abstractmethod
from simg.util import sstring
from .base import BaseDevAdapter, DevAdapterCmdError, VendorMsg


class BaseDriverAdapter(BaseDevAdapter):
    __metaclass__ = ABCMeta

    def __init__(self, adb, devpath="/sys/devices/virtual/video/sii6400"):
        self._adb = adb
        self._devpath = devpath
        self._diagpath = os.path.join(self._devpath, "diag")
        self._wihdpath = os.path.join(self._devpath, "wihd")
        self._wvanpath = os.path.join(self._wihdpath, "wvan")

    @abstractmethod
    def run(self, cmd):
        """
        This is a template method.
        See <Template Method> design pattern for detail: http://www.oodesign.com/template-method-pattern.html
        """
        pass

    def __dmesg(self):
        resp = None
        if self._adb:
            resp = self.run("dmesg -c")
        else:
            resp = self.run("dmesg | tail")
        return resp[1]

    def __diag_send(self, cmd):
        # do cleanup first
        while True:
            if not self.__diag_recv():
                break
        cmd = "echo %s > /sys/devices/virtual/video/sii6400/diag/cmd" % cmd
        self.run(cmd)

    def __diag_recv(self):
        cmd = "cat /sys/devices/virtual/video/sii6400/diag/cmd_output"
        resp = self.run(cmd)
        return resp[1]

    def sendcmd(self, cmd, timeout=5.0, interval=0.5, trim=True):
        self.__diag_send(cmd)
        startTime = time.time()
        data = None
        while True:
            time.sleep(interval)
            resp = self.__diag_recv()
            if resp:
                data = resp
                break
            else:
                if time.time() - startTime > timeout:
                    break
        return data

    def setMode(self, mode):
        self.run("echo %s > /sys/devices/virtual/video/sii6400/mode" % mode)
        logger.debug("dmesg: %s", self.__dmesg())
        resp = self.run("cat /sys/devices/virtual/video/sii6400/mode")
        return resp[1]

    def getMode(self):
        resp = self.run("cat /sys/devices/virtual/video/sii6400/mode")
        return resp[1]

    def scan(self, duration=0, interval=0):
        self.run("echo %s > /sys/devices/virtual/video/sii6400/wihd/wvan/scan_duration" % duration)
        self.run("echo %s > /sys/devices/virtual/video/sii6400/wihd/wvan/scan_interval" % interval)
        self.run("echo 1 > /sys/devices/virtual/video/sii6400/wihd/wvan/scan")
        resp = self.run("cat /sys/devices/virtual/video/sii6400/wihd/wvan/scan")
        return resp[1]

    def join(self, wvan):
        if not isinstance(wvan, list):
            raise TypeError("wvan should be a list")
        # dest = [ wvan["id"], wvan["hr"], wvan["lr"]]
        self.run("echo %s > /sys/devices/virtual/video/sii6400/wihd/wvan/join" % wvan)

    def catJoin(self):
        resp = self.run("cat /sys/devices/virtual/video/sii6400/wihd/wvan/join")
        return eval(resp[1])

    def connect(self, dstMacAddr):
        dstMacAddr = sstring.trimMacAddress(dstMacAddr)
        self.run("echo %s > /sys/devices/virtual/video/sii6400/wihd/connect" % dstMacAddr.replace(":", ""))

    def disconnect(self, timeout=3):
        self.run("echo 1 > /sys/devices/virtual/video/sii6400/wihd/disconnect")

    def upgradeFirmware(self):
        raise NotImplementedError

    def setMacAddress(self, macaddr):
        resp = self.sendcmd("custparamset 0 %s" % macaddr.replace(":", ""))
        if "OK" not in resp:
            raise DevAdapterCmdError

    def getMacAddress(self):
        resp = self.run("cat /sys/devices/virtual/video/sii6400/wihd/self/mac_addr")
        return sstring.trimMacAddress(resp)

    def setDeviceName(self, name):
        self.run("echo %s > /sys/devices/virtual/video/sii6400/wihd/self/name" % name)

    def getDeviceName(self):
        return self.run("cat /sys/devices/virtual/video/sii6400/wihd/self/name")

    def getFwVersion(self):
        resp = self.run("cat /sys/devices/virtual/video/sii6400/fw_version")
        return resp[1]

    def getFwBuild(self):
        fw_ver = self.getFwVersion()
        fw_num = re.search("(\d{5})", fw_ver).group(1)
        return str('SVN') + fw_num

    def getDevState(self):
        resp = self.run("cat /sys/devices/virtual/video/sii6400/wihd/state")
        return resp[1]

    def getLinkQuality(self):
        resp = self.run("cat /sys/devices/virtual/video/sii6400/wihd/remote_device/signal_strength")
        return resp[1]

    def setVendorMsgVendorId(self, vendorID):
        cmd = "echo %s > /sys/devices/virtual/video/sii6400/wihd/vendor_msg/vendor_id" % vendorID.replace(":", "")
        resp = self.run(cmd)
        return resp[1]

    def setVendorMsgDestMacAddr(self, dstMacAddr):
        cmd = "echo %s > /sys/devices/virtual/video/sii6400/wihd/vendor_msg/dest_mac_addr" % dstMacAddr.replace(":", "")
        resp = self.run(cmd)
        return resp[1]

    def setVendorMsgFilter(self, msgFilter):
        cmd = "echo %s > /sys/devices/virtual/video/sii6400/wihd/vendor_msg/recv_filter" % msgFilter.replace(":", "")
        resp = self.run(cmd)
        return resp[1]

    def sendVendorMsg(self, msg):
        if not isinstance(msg, VendorMsg):
            raise TypeError("msg is not a VendorMsg")
        self.setVendorMsgVendorId(msg.vendorID.replace(":", ""))
        self.setVendorMsgDestMacAddr(msg.dstMacAddr.replace(":", ""))
        cmd = "echo %s > /sys/devices/virtual/video/sii6400/wihd/vendor_msg/send" % msg.data.replace(":", "")
        resp = self.run(cmd)
        return resp[1]


class LocalDriverAdapter(BaseDriverAdapter):
    def run(self, cmd):
        if self._adb:
            cmd = '%s "%s"' % (self._adb, cmd)
        logger.debug("run: cmd=%s", cmd)
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        stdout = proc.communicate()[0]
        logger.debug("run: retcode=%s, output=\n%s", proc.returncode, stdout)
        if proc.returncode != 0:
            raise DevAdapterCmdError("command '%s' error" % cmd)
        return proc.returncode, stdout

    def exit(self):
        pass


class SSHDriverAdapter(BaseDriverAdapter):
    def __init__(self, adb, host, port=22, username=None, password=None, devpath="/sys/devices/virtual/video/sii6400"):
        BaseDriverAdapter.__init__(self, adb, devpath)
        self._sshclient = simg.net.ssh.SSHClient(host, port, username, password)

    def run(self, cmd):
        return self._sshclient.run(cmd)

    def exit(self):
        if self._sshclient:
            self._sshclient.close()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
