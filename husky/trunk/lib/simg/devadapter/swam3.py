#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import re
import time
import errno
import socket
import random
import subprocess
from abc import ABCMeta, abstractmethod

from simg.util import sstring
from base import BaseDevAdapter, VendorMsg
from base import DevAdapterError, DevAdapterCmdError

class SWAM3Connection(BaseDevAdapter):
    RECV_BUFSIZE = 4096

    def __init__(self, addr, name=""):
        logger.debug("create ss_server connection with addr: %s", addr)
        self.logname = None
        self._name = name
        self._addr = addr
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect(self._addr)
        self._sock.setblocking(0)
        self._device_type = None

    def close(self):
        if self._sock:
            self._sock.close()

    def sendcmd(self, cmd, timeout=5.0, interval=0.5, trim=True, wakeup=True):
        logger.info("send: '%s' to %s %s", cmd, self._addr, self._name)
        # Clear any data in the receive buffer first before issuing the command
        while True:
            # if a recv() call doesn’t find any data, an error exception is raised
            try:
                self._sock.recv(self.RECV_BUFSIZE)
            except socket.error:
                break

        data = ""
        starttime = time.time()
        try:
            self._sock.send(str(cmd + "<EOF>").encode("ascii"))
            # self._sock.send(str(cmd + "<EOF>"))
        except socket.error:
            logger.exception("")
        else:
            while True:
                try:
                    newdata = self._sock.recv(self.RECV_BUFSIZE)
                    logger.debug("recv: %s", newdata)
                    data += newdata.decode()
                except socket.error:
                    pass
                finally:
                    if "<EOF>" in data:
                        if "Warning:BB is in Sleep Mode" in data and wakeup is True:
                            logger.debug("Module is in sleep mode, force to wake up it")
                            self.sendcmd("pwr_set_mode 3")
                            logger.debug("retry cmd: %s", cmd)
                            data = self.sendcmd(cmd, timeout, interval, trim=False)
                        break
                    if time.time() - starttime > timeout:
                        logger.debug("recv timeout")
                        break
                    if interval:
                        time.sleep(interval)

        if trim:
            data = data.strip()
            data = data.replace("<EOF>", "")
            data = data.replace("\r", "")
        logger.info("Response: %s", data)
        return data

    def setLogFilename(self, newname):
        logger.info("change ss_server log to '%s' of the SWAM3 server on %s", newname, self._addr)
        try:
            self._sock.send(str("ss_server logfilename=%s<EOF>" % newname).encode("ascii"))
        except socket.error:
            logger.exception("change ss_server log path failed")
            raise
        else:
            logger.info("change ss_server log path done")
            self.logname = newname

    def nvramreset(self):
        self.sendcmd("nvram_set_defaults")
        self.reset()

    @abstractmethod
    def reset(self):
        raise NotImplementedError

    @abstractmethod
    def upgradeFirmware(self, filename):
        raise NotImplementedError

    def getMacAddress(self):
        mac = self.sendcmd("custparamget 0")
        if re.search("OK", mac, re.I):
            #for B&A
            mac = mac.split("OK")[0].split("=")[1]
        else:
            #for Gen3
            mac = mac.split("<")[0]
        return sstring.trimMacAddress(mac)

    def setMacAddress(self, mac):
        self.sendcmd("custparamset 0 " + mac)

    def getDeviceName(self):
        devname = self.sendcmd("custparamget 2")
        if re.search("OK", devname, re.I):
            #for B&A
            devname = devname.split("OK")[0].split("=")[1]
        else:
            #for Gen3
            devname = devname.split(" ")[0]
        return devname

    def setDeviceName(self,devname):
        self.sendcmd("custparamset 2 "+ devname)

    def connect(self, dstMacAddr=None):
        if dstMacAddr:
            dstMacAddr = dstMacAddr.lower() + ":00"
            macAddrs = self.sendcmd("dev_table_dump 2")
            R = re.compile(r"\(([^\)]*)\)")
            deviceList = re.findall(R, macAddrs)
            if deviceList:
                if dstMacAddr in deviceList:
                    index = deviceList.index(dstMacAddr)
                    self.sendcmd("connect_device " + index)
                    logger.debug("Connecting to device " + index)
                else:
                    logger.debug("The given device not in the wvan")
            else:
                logger.debug("No device in the wvan")
        else:
            self.sendcmd("connect_device 0")
            logger.debug("Connecting to device 0")

    def disconnect(self):
        self.sendcmd("disconnect_device 0")
        logger.debug("Disconnecting to device 0")

    def setVendorMsgFilter(self, msgFilter):
        return self.sendcmd("vendor_msg_set_filter %s" % msgFilter)

    def sendVendorMsg(self, msg):
        if not isinstance(msg, VendorMsg):
            raise TypeError("msg is not a VendorMsg")
        return self.sendcmd("vendor_msg_send %s %s %s %s" % (msg.vendorID, msg.dstMacAddr, msg.length, msg.data))

    def recvVendorMsg(self):
        """<15:40:52.319> 11:11:11 11:22:33:44:55:66 03 AA:BB:CC 0"""
        resp = self.sendcmd("ss_server getvendormsg")
        l = resp.split(" ")
        l = l[1:-1]
        vendorID = l[0].lower()
        dstMacAddr = sstring.trimMacAddress(l[1].lower())
        length = int(l[2])
        data = l[3].lower()
        return VendorMsg(vendorID, dstMacAddr, length, data)

    def getFwVersion(self):
        return self.sendcmd("show_version")

    def getFwBuild(self):
        fw_ver = self.getFwVersion()
        num_index = fw_ver.find('SVN') + 3
        return 'svn' + fw_ver[num_index:num_index+4]

    def getDevState(self):
        return self.sendcmd("dev_get_state")

    def getLinkQuality(self):
        link_qua = self.sendcmd("get_hr_link_quality")
        qua_index = link_qua.find('=') + 1
        return int(link_qua[qua_index:])

    def getSoftPairingStatus(self):
        resp = self.sendcmd("soft_pairing_info")
        mode = re.search(r"Soft pairing status=(\d{1})", resp).group(1)
        return int(mode)

    def getProductId(self):
        resp = self.sendcmd("custparamget 3")
        pid = re.search(r"cfgget id=([\w ]+)", resp).group(1)
        return pid

    def srvexit(self):
        logger.info("exit ss_server")
        self.sendcmd("ss_server exit", timeout=1.0)
        self.close()


class GEN3Connection(SWAM3Connection):
    def upgradeFirmware(self, filename):
        if not os.path.exists(filename):
            raise OSError(errno.ENOENT, "Firmware '%s' not exists" % filename)

        resetflag = False
        logger.debug("Querying the Enable Host bootup with BB in resetmode NVRAM (0x67) value on Gen3...")
        val = self.sendcmd("nvramget 0x67")
        if re.search("Parameter 0x67=0x01", val, re.I):
            logger.debug("Setting the Enable Host bootup with BB in resetmode NVRAM (0x67) value on Gen3 to 0...")
            self.sendcmd("nvramset 0x67 0x0")
            resetflag = True

        logger.debug("Querying the Sleep duration on inactivity (0x66) value on Gen3...")
        val = self.sendcmd("nvramget 0x66")
        if not re.search("Parameter 0x67=0x0", val, re.I):
            logger.debug("Setting the Sleep duration on inactivity (0x66) value on Gen3 to 0...")
            self.sendcmd("nvramset 0x66 0x0")
            resetflag = True

        if resetflag:
            self.reset()
            time.sleep(15)

        self.sendcmd("nvram_update_flag 0 1")
        self.sendcmd("ss_server embeddedupgrade=%s" % filename)
        self.sendcmd("nvram_update_flag 0 0")
        self.reset()
        time.sleep(15)

    def reset(self):
        return self.sendcmd("reset")


class BAConnection(SWAM3Connection):
    def upgradeFirmware(self, filename):
        """
        ERROR: AP port not opened<EOF>
        ERROR: Module not supported<EOF>
        ERROR: File not exists<EOF>
        ERROR: Open file failed<EOF>
        ERROR: Upgrade firmware failed<EOF>
        OK: Upgrade firmware succeeded<EOF>
        """
        if not os.path.exists(filename):
            raise OSError(errno.ENOENT, "Firmware '%s' not exists" % filename)

        resp = self.sendcmd("svr_apcommand full_upgrade=%s" % filename, timeout=120.0)
        try:
            match = re.search(r"ERROR: (.*)", resp)
            if match:
                raise DevAdapterCmdError(match.group(1))
        finally:
            self.reset()

    def reset(self):
        return self.sendcmd("svr_apcommand reset")


class SWAM3Server(object):
    BINPATH = "C:/Program Files (x86)/Silicon Image/SWAM3/SWAM3.exe"

    def __init__(self, moduleid, tcpport, ap_moduleid=None, logname=None):
        self._moduleid = moduleid
        self._tcpport = int(tcpport)
        self._logname = logname
        self._ap_moduleid = ap_moduleid
        self._srvproc = None    # will be set when calling self.start

    def __check_addr_not_in_use(self):
        addr = ("0.0.0.0", self._tcpport)
        logger.info("check addr <%s:%s> is not in use before startup ss_server" % addr)
        sock = socket.socket()
        try:
            sock.bind(addr)
        finally:
            sock.close()

    def __check_ss_server_avaiable(self):
        logger.debug("check ss_server is avaiable with cmd: show_version ")
        Connection = BAConnection if self._ap_moduleid else GEN3Connection
        conn = Connection(addr=("127.0.0.1", self._tcpport))
        try:
            if not conn.sendcmd("show_version"):
                conn.sendcmd("ss_server exit", timeout=1.0)
                raise DevAdapterError("startup ss_server failed")
        finally:
            conn.close()

    def start(self):
        self.__check_addr_not_in_use()

        cmd = '"%s" server --moduleid=%s --portno=%s --logsendtoclient=0 --logtoconsole=0 --start=1' % (self.BINPATH, self._moduleid, self._tcpport)
        if self._logname:
            cmd += " --logfilename=%s" % self._logname
        if self._ap_moduleid:
            cmd += " --ap_moduleid=%s" % self._ap_moduleid
        logger.info("startup ss_server with cmd: %s", cmd)
        self._srvproc = subprocess.Popen(cmd)
        time.sleep(15)

        self.__check_ss_server_avaiable()

    def stop(self):
        conn = SWAM3Connection(addr=("127.0.0.1", self._tcpport))
        conn.srvexit()
        if self._srvproc:
            self._srvproc.terminate()


class LocalSWAM3Adapter(object):
    def __init__(self, moduleid, ap_moduleid=None, tcpport=None, logname=None, name=""):
        if not tcpport:
            while True:
                sock = socket.socket()
                port = random.randint(40000, 65535)
                addr = ("0.0.0.0", port)
                try:
                    sock.bind(addr)
                except socket.error as err:
                    if err.errno == errno.EADDRINUSE:
                        logger.debug("addr <%s:%s> is in use, random another port")
                        continue
                    else:
                        raise
                else:
                    tcpport = port
                    break
                finally:
                    sock.close()

        tcpport = int(tcpport)
        srv = SWAM3Server(moduleid, tcpport, ap_moduleid, logname)
        srv.start()

        Connection = BAConnection if ap_moduleid else GEN3Connection
        self.conn = Connection(("127.0.0.1", tcpport), name)

    def __getattribute__(self, name):
        """
        Check the calling method name:
        If it is 'conn' or 'close', return self.conn or self.close; otherwise redirect it to self.conn
        This is an implementation of <Proxy> design pattern
        See <Proxy> design pattern for detail: http://www.oodesign.com/proxy-pattern.html
        """
        if name == "conn":
            return object.__getattribute__(self, "conn")
        elif name == "close":
            return object.__getattribute__(self, "close")
        else:
            conn = object.__getattribute__(self, "conn")
            return getattr(conn, name)

    def close(self):
        logger.info("exit ss_server")
        self.sendcmd("ss_server exit", timeout=1.0)
        self.conn.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )

    adapter = LocalSWAM3Adapter("ba", "ba_ap", 40000, name="BA SRC1")
    adapter.close()
    # filename = r"H:\flash_wihd_mhl_int.bin"
    # adapter.upgradeFirmware(filename)
