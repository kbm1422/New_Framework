#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import sys
import time

import simg.os.common as oscommon
import simg.io.file as fs
import simg.io.text as Text

#import socket
# import fcntl
# import struct
# import encodings.idna
# 
# def getaddrbyifname(ifname):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     info = socket.inet_ntoa( fcntl.ioctl( sock.fileno(), 0x8915, struct.pack('256s', ifname[:15]) ) )
#     return info[20:24]


def sethostname(name):
    oscommon.runex("hostname %s" % name)
    txt = Text.TextEditor("/etc/sysconfig/network")
    txt.set_param("HOSTNAME", name)
    txt.save()


def mount(source, target, fstype, fstab=False):
    logger.debug("mount: source=%s, target=%s, fstype=%s, fstab=%s", source, target, fstype, fstab)

    (retcode, mount_info) = oscommon.run("mount")
    if retcode != 0:
        raise Exception("can't run 'mount' command")
    if source in mount_info:
        logger.debug("%s is already mounted" % source)
    else:
        oscommon.runex("mount -t %s %s %s" % (fstype, source, target))
    
    if fstab:
        txt = Text.TextEditor("/etc/fstab")
        txt.delete(target)
        txt.insert( "%s %s    %s    defaults    0 0" % (source, target, fstype) )
        txt.save()


def umount(target, fstab=True):
    logger.debug("umount: target=%s, fstab=%s", target, fstab)

    (retcode, mount_info) = oscommon.run("mount")
    if retcode != 0:
        raise Exception("can't run 'mount' command")
    if target in mount_info:
        oscommon.runex("umount %s" % target)
    else:
        logger.debug("target %s is not mounted", target)
    
    if fstab:
        txt = Text.TextEditor("/etc/fstab")
        txt.delete(target)
        txt.save()


def disable_selinux():
    txt = Text.TextEditor("/etc/sysconfig/selinux")
    txt.set_param("SELINUX", "disabled")
    txt.save()
    oscommon.run("setenforce 0")


def disable_firewall():
    svc = oscommon.Service("iptables")
    svc.stop()
    svc.config(autostart=False)


import abc
import atexit
import signal

class Daemon(object):
    """
    A generic daemon class.
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile=None, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):  
        self.stdin = stdin  
        self.stdout = stdout  
        self.stderr = stderr  
        self.pidfile = pidfile or "/var/run/%s.pid" % self._svc_name_
      
    def daemonize(self):  
        """ 
        do the UNIX double-fork magic, see Stevens' "Advanced  
        Programming in the UNIX Environment" for details (ISBN 0201563177) 
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16 
        """  
        try:
            pid = os.fork()
            if pid > 0:  
                # exit first parent  
                sys.exit(0)   
        except OSError as e:   
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))  
            sys.exit(1)  
      
        # decouple from parent environment  
        os.chdir("/")   
        os.setsid()   
        os.umask(0)   
      
        # do second fork  
        try:   
            pid = os.fork()   
            if pid > 0:  
                # exit from second parent
                sys.exit(0)   
        except OSError as e:   
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))  
            sys.exit(1)   
      
        # redirect standard file descriptors  
        sys.stdout.flush()  
        sys.stderr.flush()  
        si = open(self.stdin, 'r')  
        so = open(self.stdout, 'a+')  
        se = open(self.stderr, 'a+', 0)  
        os.dup2(si.fileno(), sys.stdin.fileno())  
        os.dup2(so.fileno(), sys.stdout.fileno())  
        os.dup2(se.fileno(), sys.stderr.fileno())  
        
        si.close()
        so.close()
        se.close()
      
        # write pidfile
        atexit.register(self.delpid)  
        pid = str(os.getpid())
        with open(self.pidfile,'w+') as pf:
            pf.write("%s\n" % pid)
      
    def delpid(self):  
        os.remove(self.pidfile)  
        
    def start(self):
        # Check for a pidfile to see if the daemon already runs  
        try:  
            pf = file(self.pidfile,'r')  
            pid = int(pf.read().strip())  
            pf.close()  
        except IOError:  
            pid = None  
      
        if pid:  
            message = "pidfile %s already exist. Daemon already running?\n"  
            sys.stderr.write(message % self.pidfile)  
            sys.exit(1)  

        self.daemonize()  
        self.run()
        
    def stop(self):
        # Get the pid from the pidfile  
        try:  
            pf = open(self.pidfile,'r')  
            pid = int(pf.read().strip())  
            pf.close()  
        except IOError:  
            pid = None  
      
        if not pid:  
            message = "pidfile %s does not exist. Daemon not running?\n"  
            sys.stderr.write(message % self.pidfile)  
            return # not an error in a restart  
        # Try killing the daemon process      
        try:  
            while 1:  
                os.kill(pid, signal.SIGTERM)  
                time.sleep(0.1)  
        except OSError as err:  
            err = str(err)  
            if err.find("No such process") > 0:  
                if os.path.exists(self.pidfile):  
                    os.remove(self.pidfile)  
            else:  
                print(str(err))  
                sys.exit(1)  
    
    
    def restart(self):  
        self.stop()  
        self.start()  
        
    @abc.abstractmethod
    def run(self):
        """ 
        You should override this method when you subclass Daemon. It will be called after the process has been 
        daemonized by start() or restart(). 
        """  

class DaemonService(object):
    _svc_tmpl_ = """#!/bin/sh
#
# chkconfig: 2345 86 14
#
# description: Daemon Service to support deployment

if [ -f /etc/init.d/functions ] ; then
  . /etc/init.d/functions
elif [ -f /etc/rc.d/init.d/functions ] ; then
  . /etc/rc.d/init.d/functions
else
  exit 0
fi

RETVAL=0

prog="service_name"
args=""
binary=/xormedia/build/xdeploy/xagent/dist/DeployAgent
pidfile=/var/run/${prog}.pid

start() {
    echo -n $"Starting ${prog} services: "
    if [ -f $pidfile ] ; then
        rm -f $pidfile
    fi
    daemon --pidfile=$pidfile $binary $args
    RETVAL=$?
    echo
    [ $RETVAL -eq 0 ] && touch /var/lock/subsys/${prog} || RETVAL=1
    return $RETVAL
}    

stop() {
    echo -n $"Shutting down ${prog} services: "
    killproc -p $pidfile $binary
    RETVAL=$?
    echo
    [ $RETVAL -eq 0 ] && rm -f /var/lock/subsys/${prog}
    return $RETVAL
}    


case "$1" in
    start)
        ps_log=`mktemp /var/tmp/ps.log.XXXXXX`
        ps aux --cols 1024 >"ps_log"
        if grep $binary "ps_log" >/dev/null 2>/dev/null ; then
            echo "${prog} service is up and running, no need start this service again"
        else
            start
        fi
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    status)
        status ${prog}
        ;;
    *)
        echo $"Usage: $0 {start|stop|restart|status}"
        exit 1
esac
exit $RETVAL
""" 
    
    def __init__(self, cls):
        self.svc_name   = cls._svc_name_
        self.svc_loct = "/etc/init.d/%s" % self.svc_name
        self._txt = Text.TextEditor()

    def create(self, **kwargs):
        if not os.path.exists(self.svc_loct):
            self._txt.load(text=self._svc_tmpl_)
            self._txt.set_param("prog", self.svc_name)
            self._txt.save(file=self.svc_loct)
            fs.chmod(self.svc_loct, 0o755)
        self.config(**kwargs)
        
        os.system("chkconfig --add %s" % self.svc_name)

    def delete(self):
        os.system("chkconfig --del %s" % self.svc_name)
        if os.path.exists(self.svc_loct):
            fs.remove(self.svc_loct)

    def config(self, svc_desp=None, exe_name=None, exe_args=None, startup=None):
        exe_name = exe_name or os.path.realpath(sys.argv[0])
        
        self._txt.load(file=self.svc_loct)
        self._txt.set_param("binary", '%s' % exe_name)
        if exe_args is not None:
            self._txt.set_param("args", '"%s"' % exe_args)
        if exe_args is not None:
            self._txt.set_param("description", svc_desp, '%(name)s: %(value)s')
        self._txt.save()
        
        if startup is not None:
            if startup:
                os.system("chkconfig %s on" % self.svc_name)
            else:
                os.system("chkconfig %s off" % self.svc_name)


class Rpm(object):
    def __init__(self, pkg, ver=None):
        self.pkg = pkg
        self.ver = "-%s" % ver if ver else ""
        self.name = "%s%s" % (self.pkg, self.ver)
        
    def install(self, dirpath, nodeps=False, retry=3):
        cmd = "rpm -ivh"
        if nodeps:
            cmd += " --nodeps"
        cmd += " %s*" % self.name
        
        while True:
            retcode = oscommon.run(cmd, dirpath)[0]
            if retcode == 0:
                break
            else:
                if retry > 0:
                    logger.info("rpm package [%s] installed failed. uninstall it and retry.", self.name)
                    self.uninstall()
                    retry = retry - 1
                    continue
                else:
                    raise Exception("failed to install: %s" % self.name)
        logger.info("rpm package [%s] installed successfully.", self.name)

    def upgrade(self, dirpath):
        pass
    
    def uninstall(self):
        retcode = oscommon.run("rpm -q %s" % self.pkg)[0]
        if retcode == 0:
            oscommon.runex("rpm -q %s | xargs rpm -e --allmatches --noscripts --nodeps" % self.pkg)
        else:
            logger.info("don't find rpm [%s] installed", self.name)

if __name__=="__main__":
    logging.basicConfig(
        level = logging.DEBUG, 
        format= '%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )