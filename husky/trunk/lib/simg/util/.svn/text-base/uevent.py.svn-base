#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import re
import time
import json
import subprocess
from Queue import Queue, Empty

import socket
import threading

from collections import namedtuple
from abc import ABCMeta, abstractmethod

Event = namedtuple("Event", ["type", "data", "timestamp"])


class BaseUeventSubject(object):
    """
    See <Observer> design pattern for detail: http://www.oodesign.com/observer-pattern.html
    See <Template Method> design pattern for detail: http://www.oodesign.com/template-method-pattern.html
    """
    __metaclass__ = ABCMeta
    
    def __init__(self):
        self._listeners = []
        self._mutex = threading.RLock()
        self._shouldstop = threading.Event()
        self._thread = threading.Thread(target=self._notify)
    
    def start(self):
        self._shouldstop.clear()  # must clear self._shouldstop for situation start -> stop -> start, if not clear, self._notify will not be running
        self._thread.start()
    
    def stop(self):
        self._shouldstop.set()
        self._thread.join()
    
    @abstractmethod
    def _notify(self):
        pass

    def listen(self, etype):
        listener = Listener(etype, self)
        self.attach(listener)
        return listener

    def attach(self, listener):
        with self._mutex:
            self._listeners.append(listener)  
    
    def detach(self, listener):
        with self._mutex:
            if listener in self._listeners:
                self._listeners.remove(listener)


class UeventSocketSubject(BaseUeventSubject):
    NETLINK_KOBJECT_UEVENT = 15

    def _notify(self):
        sock = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, self.NETLINK_KOBJECT_UEVENT)
        try:
            sock.setblocking(0)
            sock.bind((0, 1))
            while not self._shouldstop.is_set():
                try:
                    s = sock.recv(4096)
                except socket.error:
                    pass
                else:
                    timestamp = round(time.time(), 3)
                    founds = re.findall(r"_EVENT=(\{.*\})", s)
                    for found in founds:
                        try:
                            devent = json.loads(found)
                            event = Event(devent["event"], devent["data"], timestamp)
                            
                            with self._mutex:
                                for listener in self._listeners:
                                    if event.type == listener.type:
                                        listener.queue.put(event)
                        except KeyboardInterrupt:
                            raise
                        except (ValueError, TypeError):
                            logger.exception("")
        finally:
            sock.close()


class UeventLogSubject(BaseUeventSubject):
    def __init__(self, adb, logname="/home/ba/scripts/uevent.log"):
        BaseUeventSubject.__init__(self)
        self._adb = adb
        self._logname = logname
        
    def start(self):
        if os.path.exists(self._logname):
            os.remove(self._logname)
            
        logger.debug("start up uevent listen")
        if self._adb:
            self._proc = subprocess.Popen("adb shell /lib/firmware/ueventListen > %s" % self._logname, shell=True)
        else:
            self._proc = subprocess.Popen("./uevent_listen", cwd="/home/ba/scripts")
        
        # make sure the log file is exist
        with open(self._logname, "w") as logfile:
            logfile.write("")
        BaseUeventSubject.start(self)  

    def stop(self):
        BaseUeventSubject.stop(self)
        try:
            self._proc.terminate()
        except NameError as err:
            logger.error("handle jython error: %s, try to kill it with shell command", str(err))
            if self._adb:
                resp = os.system("adb shell ps | grep ueventListen")
                if resp == 0:
                    resp = os.popen("adb shell ps ueventListen").readlines()
                    pid = resp[1].split()[1]
                    os.system("adb shell kill " + pid)
            else:
                os.system("killall uevent_listen")

    def _notify(self):
        while not self._shouldstop.is_set():
            lines = None
            with open(self._logname, "r") as logfile:
                lines = logfile.readlines()
            
            if lines:
                for index in range(len(lines)):   
                    matchedEvent = re.search(r"_EVENT=(.*)", lines[index])
                    if matchedEvent:
                        try:
                            devent = json.loads(matchedEvent.group(1))
                            matchedTimestamp = re.search(r"\[(\d+)\]", lines[index - 4])
                            timestamp = int(matchedTimestamp.group(1))
                            
                            event = Event(devent["event"], devent["data"], timestamp)
                            with self._mutex:
                                for listener in self._listeners:
                                    if event.type == listener.type:
                                        listener.queue.put(event)
                        except KeyboardInterrupt:
                            raise
                        except (ValueError, TypeError):
                            logger.exception("")
            time.sleep(0.1)


class Listener(object):
    def __init__(self, etype, subject):
        self.type = etype
        self.queue = Queue()
        self.subject = subject
        
    def get(self, block=True, timeout=None):
        try:
            event = self.queue.get(block, timeout)
            self.queue.task_done()
            logger.debug("%s recv event: %s", self, event)
            return event
        except Empty:
            return None
    
    def __repr__(self):
        return "<UeventListener '%s'>" % self.type

    def __str__(self):
        return self.__repr__()
    
    def __enter__(self):
        logger.debug("%s ENTER", self)
        return self
        
    def __exit__(self, t, v, tb):
        logger.debug("%s EXIT", self)
        self.subject.detach(self)


class UeventListener(object):
    """
    @deprecated: 
    """
    def __init__(self, adb, logname="/home/ba/scripts/uevent.log"):
        self._adb = adb
        self._logname = logname
    
    def start(self):
        if os.path.exists(self._logname):
            os.remove(self._logname)
        
        if self._adb:
            subprocess.Popen("adb shell /lib/firmware/ueventListen > %s" % self._logname, shell=True)
        else:
            logger.debug("start uevent_listen")
            subprocess.Popen("./uevent_listen", cwd="/home/ba/scripts")
        time.sleep(2)

    def stop(self):
        if self._adb:
            resp = os.system("adb shell ps | grep ueventListen")
            if resp == 0:
                resp = os.popen("adb shell ps ueventListen").readlines()
                pid = resp[1].split()[1]
                os.system("adb shell kill " + pid)
        else:
            os.system("killall uevent_listen")
    
    def getAllEvents(self):
        events = []
        ftxt = open(self._logname, "r")
        lines = ftxt.readlines()
        ftxt.close()
        for index in range(len(lines)):       
            matchEvent = re.search(r"_EVENT=(.*)", lines[index])
            if matchEvent:
                eventstr = matchEvent.group(1)
                event = {}
                if "custparamsetbulk" in eventstr:
                    re.search(r'"data":\[(.*)\]', eventstr)
                else:
                    event = json.loads(eventstr)
                matchTimestamp = re.search(r"\[(\d+)\]", lines[index - 4])
                timestamp = int(matchTimestamp.group(1))
                event["timestamp"] = timestamp
                events.append(event)
        return events           
    
    def getEventsByTimeStamp(self, timestamp):
        return self.getEventsByTimeRange(timestamp, timestamp)

    def getEventsByTimeRange(self, starttime, stoptime=None):
        events = []
        if stoptime is None:
            stoptime = time.time()    
        for event in self.getAllEvents():
            if int(starttime) <= event["timestamp"] <= int(stoptime):
                events.append(event)
        return events

    def getEventsByType(self, eventType):
        events = []
        for event in self.getAllEvents():
            if event["event"] == eventType:
                events.append(event)
        return events

    def getEventsByTypeAndTimeRange(self, eventType, fromTime, toTime=None):
        logger.debug("getEventsByTypeAndTimeRange: eventType=%s, fromTime=%s, toTime=%s", eventType, fromTime, toTime)
        events = []
        if toTime is None:
            toTime = time.time()
        for event in self.getAllEvents():
            if int(fromTime) <= event["timestamp"] <= int(toTime) and event["event"] == eventType:
                events.append(event)
        logger.debug("found events: %s", events)
        return events

    def getEventsByTypeAndTimeRangeWithTimeout(self, eventType, fromTime, toTime=None, interval=0.1, timeout=3):
        logger.debug("getEventsByTypeAndTimeRangeWithTimeout: eventType=%s, fromTime=%s, toTime=%s, interval=%s, timeout=%s", eventType, fromTime, toTime, interval, timeout)
        starttime = time.time()
        events = []
        while True:
            events = self.getEventsByTypeAndTimeRange(eventType, fromTime, toTime)
            if events:
                break
            if time.time() - starttime > timeout:
                logger.debug("timeout reached when getEventsByTypeAndTimeRangeWithTimeout")
                break
            time.sleep(interval)
        return events
    
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
#     ue = UEventService("")
#     
#     queue1 = ue.newListener("wvan_scan_started")
#     queue2 = ue.newListener("wvan_scan_complete")
#     ue.start()
#     print "wvan_scan_started", queue1.get()
#     print "wvan_scan_complete", queue2.get()
#     ue.stop()
