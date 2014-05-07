#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import re
import posixpath

import ftplib


class FTPClient(ftplib.FTP):
    def put(self, lsrc, rdst, exclude=None):
        logger.info("ftp put: lsrc=[%s], rdst=[%s], exclude=[%s]", lsrc, rdst, exclude )
        def putdir(lsrc, rdst, exclude):
            self.mkpath(rdst)
            for name in os.listdir(lsrc):
                lsrcname = os.path.join(lsrc, name)
                if exclude and re.search(exclude, lsrcname):
                    logger.info("ftp put: skip %s", lsrcname )
                    continue
                rdstname = posixpath.join(rdst, name)
                if os.path.isdir(lsrcname):
                    putdir(lsrcname, rdstname, exclude)
                else:
                    logger.debug("ftp put: %s -> %s", lsrcname, rdstname )
                    self.cwd(rdst)
                    fileobj = open(lsrcname, "rb")
                    self.storbinary("STOR %s" % name, fileobj)
                    fileobj.close()
        
        if os.path.isdir(lsrc):
            putdir(lsrc, rdst, exclude)
        else:            
            rdstpath = None
            name = os.path.basename(lsrc)
            if self.exists(rdst):
                if self.isdir(rdst):
                    rdstpath = posixpath.join(rdst, name)
                else:
                    rdstpath = rdst
            else:
                if rdst.endswith("/"):
                    self.mkpath(rdst)
                    rdstpath = posixpath.join(rdst, name)
                else:
                    self.mkpath(os.path.dirname(rdst))
                    rdstpath = rdst
            logger.debug("ftp put: %s -> %s", lsrc, rdstpath)
            
            head, tail = posixpath.split(rdstpath)
            self.cwd(head)
            fileobj = open(lsrc, "rb")
            self.storbinary("STOR %s" % tail, fileobj)
            fileobj.close()
    
    def get(self, rsrc, ldst, exclude=None):
        raise NotImplementedError

    def mkpath(self, path):
        if self.exists(path):
            if self.isdir(path):
                logger.debug("ftp mkpath: exists '%s', type is dir, skip", path)
            else:
                raise Exception("ftp mkpath failed, path '%s' already exists, type is not dir" % path)
        else:
            logger.debug("ftp mkpath: non-exists '%s' ", path)
            head = os.path.split(path)[0]
            if self.exists(head):
                self.mkd(path)
            else:
                self.mkpath(head)
                self.mkd(path)

    def exists(self, path):
        try:
            self.sendcmd("STAT %s" % path)
            return True
        except:
            return False
    
    def isdir(self, path):
        try:
            self.cwd(path)
            return True
        except:
            return False

if __name__=="__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )