#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

import re
import time


class LogParser(object):
    def __init__(self, filename, timefmt):
        self.__filename = filename
        self.__timefmt = timefmt
        self.__timelen = len(self.__timefmt) + 1

    def findall(self, pattern):
        if not isinstance(pattern, re._pattern_type):
            pattern = re.compile(pattern)
        lines = []
        with open(self.__filename, "r") as logfile:
            for line in logfile:
                if line.search(pattern):
                    lines.append(line)
        return lines
        
    def getLineTimestamp(self, line):
        timestr = line[0:self.__timelen]
        timestamp = time.mktime(time.strptime(timestr, self.__timefmt))
        return timestamp

    def get(self, pattern, fromtime=None, timeout=None):
        if fromtime is None:
            fromtime = time.time()
        lines = []
        starttime = time.time()
        while True:
            for line in self.findall(pattern):
                if fromtime <= self.getLineTimestamp(line):
                    lines.append(line)
            
            if lines:
                break
 
            if time.time() - starttime > timeout:
                break
        return lines


class SWAM3LogParser(object):
    def __init__(self, filename):
        self._logparser = LogParser(filename, "%m/%d/%Y %H:%M:%S")
    
    def getTimestamps(self, pattern, fromtime, timeout=None):
        timestamps = []
        for logline in self._logparser.get(pattern, fromtime, timeout):
            timestamps.append(self.getLineTimestamp(logline))
        return timestamps        
    
    def getConnectTimestamps(self, fromtime, timeout=None):
        return self.getTimestamps("baseband video UNMUTE", fromtime, timeout)
            
    def getDisconnectTimestamps(self, fromtime, timeout=None):
        return self.getTimestamps("Disconnect", fromtime, timeout)    

if __name__ == "__main__":
    pass
