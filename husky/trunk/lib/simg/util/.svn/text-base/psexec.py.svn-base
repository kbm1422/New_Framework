#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

import simg.os as OS


class PsExec(object):
    def __init__(self, host, user, password, timeout=10):
        self.__host = host
        self.__user = user
        self.__password = password
        self.__timeout = timeout

    
    def run(self, cmd, cwd=None, copy=False, interactive=True):
        command = "psexec.exe \\\\%s -s -u %s -p %s" % (self.__host, self.__user, self.__password)
        if copy:
            command += " -c -f"
        if cwd:
            command += " -w %s" % cwd
        if not interactive:
            command += " -d"
        command += " -n %s %s" % (self.__timeout, cmd)
        logger.debug("psexec command: %s", command)
        return OS.run(command)
    
if __name__=="__main__":
    logging.basicConfig(
        level = logging.DEBUG, 
        format= '%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )