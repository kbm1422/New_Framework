#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import re
import posixpath
import stat
import errno

import paramiko

import simg.io.file as fs


class SSHError(Exception):
    pass


class SSHClient(paramiko.SSHClient):
    def __init__(self, *args, **kwargs):
        """the *args and **kwargs is same as method connect, if provide, the constructor will automatic call connect method
           the params listed as below:
                hostname, port=22, username=None, password=None, 
                pkey=None, key_filename=None, timeout=None, 
                allow_agent=True, look_for_keys=True, compress=False, sock=None
        """
        paramiko.client.SSHClient.__init__(self)
        if args or kwargs:
            self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.connect(*args, **kwargs)
    
    def open_sftp(self):
        return SFTPClient.from_transport(self._transport)

    def run(self, cmd, cwd=None):
        if cwd is not None:
            cmd = "cd %s && %s" % (cwd, cmd)
        ret = self.exec_command(cmd)
        stdout = ret[1]
        stderr = ret[2]
        
        full = str()
        for out in stdout.read():
            full += out
        for err in stderr.read():
            full += err
        retcode = stdout.channel.recv_exit_status()
        return (retcode, full)


class SFTPClient(paramiko.SFTPClient):
    def find(self, path, bydepth=True, exclude=None, topdir=True):
        """
        @:param bydepth: Reports the name of a directory only AFTER all its entries have been reported
        @:param exclude: a string or re pattern type, use this to exclude the path you don't want to find
        @:param topdir: whether include the topdir path
        """
        def walk(dirpath, bydepth, exclude):
            for name in self.listdir(dirpath):
                found = posixpath.join(dirpath, name)
                if exclude and re.search(exclude, found):
                    logger.info("walk: skip %s", found)
                else:
                    logger.debug("walk: process %s", found)
                    if not bydepth:
                        yield found
                    if self._isdir(found):
                        for x in walk(found, bydepth, exclude):
                            yield x
                    if bydepth:
                        yield found
        
        if self._isdir(path):
            if topdir and not bydepth:
                yield path
            for x in walk(path, bydepth, exclude):
                yield x
            if topdir and bydepth:
                yield path
        else:
            yield path

    def scp_get(self, rsrc, ldst, exclude=None):
        logger.info("scp get: rsrc=%s, ldst=%s, exclude=%s", rsrc, ldst, exclude)

        if exclude is not None and not isinstance(exclude, re._pattern_type):
            exclude = re.compile(exclude)

        def getdir(rsrc, ldst, exclude):
            fs.mkpath(ldst)
            for name in self.listdir(rsrc):
                rsrcname = posixpath.join(rsrc, name)
                if exclude and exclude.search(rsrcname):
                    logger.info("scp get: skip %s", rsrcname)
                    continue
                ldstname = os.path.join(ldst, name)
                if self._isdir(rsrcname):
                    getdir(rsrcname, ldstname, exclude)
                else:
                    logger.debug("scp get: %s -> %s", rsrcname, ldstname)
                    self.get(rsrcname, ldstname)
                                
        if self._isdir(rsrc):
            getdir(rsrc, ldst, exclude)
        else:
            ldstpath = None
            name = os.path.basename(rsrc)
            if os.path.exists(ldst):
                if os.path.isdir(ldst):
                    ldstpath = posixpath.join(ldst, name)
                else:
                    ldstpath = ldst
            else:
                if ldst.endswith("\\") or ldst.endswith("/"):
                    fs.mkpath(ldst)
                    ldstpath = posixpath.join(ldst, name)
                else:
                    fs.mkpath(os.path.dirname(ldst))
                    ldstpath = ldst
            logger.debug("scp get: %s -> %s", rsrc, ldstpath)
            self.get(rsrc, ldstpath)
            
    def scp_put(self, lsrc, rdst, exclude=None):
        logger.info("scp put: lsrc=%s, rdst=%s, exclude=%s", lsrc, rdst, exclude)

        if exclude is not None and not isinstance(exclude, re._pattern_type):
            exclude = re.compile(exclude)

        def putdir(lsrc, rdst, exclude):
            self.mkpath(rdst)
            for name in os.listdir(lsrc):
                lsrcname = os.path.join(lsrc, name)
                if exclude and exclude.search(lsrcname):
                    logger.info("scp put: skip %s", lsrcname)
                    continue
                rdstname = posixpath.join(rdst, name)
                if os.path.isdir(lsrcname):
                    putdir(lsrcname, rdstname, exclude)
                else:
                    logger.debug("scp put: %s -> %s", lsrcname, rdstname)
                    self.put(lsrcname, rdstname)            
        
        if os.path.isdir(lsrc):
            putdir(lsrc, rdst, exclude)
        else:
            name = os.path.basename(lsrc)
            if self.exists(rdst):
                if self._isdir(rdst):
                    rdstpath = posixpath.join(rdst, name)
                else:
                    rdstpath = rdst
            else:
                if rdst.endswith("\\") or rdst.endswith("/"):
                    self.mkpath(rdst)
                    rdstpath = posixpath.join(rdst, name)
                else:
                    self.mkpath(os.path.dirname(rdst))
                    rdstpath = rdst
            logger.debug("scp put: %s -> %s", lsrc, rdstpath)
            self.put(lsrc, rdstpath)

    def _isdir(self, path):
        try:
            return stat.S_ISDIR(self.stat(path).st_mode)
        except IOError:
            return False

    def exists(self, path):
        try:
            self.stat(path)
        except IOError as ioerr:
            if ioerr.errno == errno.ENOENT:
                return False
            raise
        else:
            return True

    def mkpath(self, path, mode=0o777):       
        if self.exists(path):
            if self._isdir(path):
                logger.debug("mkpath: exists '%s', type is dir, skip", path)
            else:
                raise SSHError("mkpath failed, path '%s' already exists, type is not dir" % path)
            return
        else:
            logger.debug("mkpath: non-exists '%s' ", path)
            head, tail = os.path.split(path)
            if not tail:   # no tail when xxx/newdir
                head, tail = os.path.split(head)
            if head and tail:
                self.mkpath(head, mode)
                if tail != os.path.curdir:   # xxx/newdir/. exists if xxx/newdir exists
                    logger.info("mkpath: path=%s, mode=%s", path, mode)
                    self.mkdir(path, mode)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
    
    ssh = SSHClient("192.168.1.7", username="root", password="itvitv")
    ret = ssh.run("set")
    print(ret[1])
    
    #ret = ssh.run("set")
#     ret = ssh.run("/opt/python27/bin/python /opt/python27/lib/python2.7/site-packages/simg/test/devadapter/swam3.py")
#     while True:
#         if ret[1].channel.exit_status_ready():
#             break
#         
#         if ret[1].channel.recv_ready():
#             print(ret[1].channel.recv(1024))