#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import re
import sys
import locale
import time
import subprocess
import socket

import simg.io.file as File
import simg.io.text as Text


def run(cmd, cwd=None):
    logger.debug("run: cmd=%s, cwd=%s", cmd, cwd)
   
    #stderr=subprocess.STDOUT indicate the stderr data will send to the handle of stdout
    
    #pythonw.exe starts a daemon process which doesn't have the normal access to the standard file descriptors. 
    #The only thing you would need to do in your script is to specifically set the 3rd fd for stdin:
    proc = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    
    #communicate wait and cache all stdout and stdin data until the process terminate
    stdout = proc.communicate()[0]

    logger.debug("run: retcode=%s, output=\n%s", proc.returncode, stdout)
    return (proc.returncode, stdout)
    
    
def runex(cmd, cwd=None, retry=3, interval=10, xmlrpc=True):
    while True:
        retcode, stdout = run(cmd, cwd)
        encoding = locale.getdefaultlocale()[1]
        if retcode == 0:
            return stdout.decode(encoding) if xmlrpc else stdout
        else:
            if retry > 0:
                logger.info("fail and retry(%s): [%s] at %s", retry, cmd, cwd)
                time.sleep(interval)
                retry -= 1
                continue
            else:
                #if stdout is chinese and assign it to Exception, the xmlrpc call will failed, the solution is encode it to utf-8
                errmsg = stdout.decode(encoding).encode("utf-8") if xmlrpc else stdout
                raise Exception("fail to run: [%s] at %s, code %s, message %s" % (cmd, cwd, retcode, errmsg))


def adduser(name, password, group=None):
    logger.info("add user: name=[%s], password=[%s], group=[%s]", name, password, group )
    if sys.platform == 'win32':
        group = group or "Administrators"
        ret_adduser = run("net user %s %s /add /passwordchg:no" % (name, password))
        retcode = ret_adduser[0]
        if retcode == 0:
            logger.debug("success to add user '%s'", name)
        elif retcode == 2:
            logger.debug("user '%s' already exists", name)
        else:
            raise Exception("fail to add user '%s', errmsg: %s %s" % (name, ret_adduser[1]))
        
        ret_setexpired = run('ECHO EXIT|wmic useraccount where Name="%s" set PasswordExpires=FALSE' % name)
        if 'Name="%s"' % name not in ret_setexpired[1]:
            raise Exception("fail to change user %s(PasswordExpires=FALSE)." % name)
        
        ret_setsvcright = run('ntrights.exe -u %s +r SeServiceLogonRight' % name)
        if ret_setsvcright[0] != 0:
            raise Exception("fail to grant 'log on as a service' to %s user." % name)
        
        ret_setgroup = run('net localgroup %s %s /add' % (group, name))
        if ret_setgroup[0] != 0:
            raise Exception("fail to add %s user to %s group." % (name, group))
        
        run('ECHO EXIT|wmic useraccount where Name="%s" list' % name)
        if os.path.exists("TempWmicBatchFile.bat"):
            os.remove("TempWmicBatchFile.bat")
            
    elif sys.platform.startswith('linux'):
        group = group or "root"
        ret_adduser = run("adduser %s" % name)
        if ret_adduser[0] != 0:
            raise Exception("fail to set user, errmsg: %s %s" % ret_adduser[1])
        
        ret_setpasswd = run("echo %s | passwd --stdin %s" % (password, name))
        if ret_setpasswd[0] != 0:
            raise Exception("fail to set password, errmsg: %s %s" % ret_setpasswd[1])
        
        ret_setgroup = run("usermod -G %s %s" % (group, name))
        if ret_setgroup[0] != 0:
            raise Exception("fail to add '%s' into '%s' group, errmsg: %s %s" % (name, group, ret_setgroup[1]))                
    else:
        pass


def deluser(name):
    if sys.platform == 'win32':
        ret = run("net user %s /delete" % name)
        retcode = ret[0]
        if retcode == 0:
            logger.info("success to delete user '%s'", name)
        elif retcode == 2:
            logger.info("user '%s' not exists", name)
        else:
            raise Exception("fail to delete user '%s', errmsg: %s %s" % (name, ret[1]))
    elif sys.platform.startswith('linux'):
        ret = run("userdel %s" % name)
        retcode = ret[0]
        if retcode == 0:
            logger.info("success to delete user '%s'", name)
        elif retcode == 1536:
            logger.info("user '%s' not exists", name)
        else:
            raise Exception("fail to delete user '%s', errmsg: %s %s" % (name, ret[1]))
    else:
        pass


def getlocaladdr(remote, port):
    addr = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((remote, port))
        addr = sock.getsockname()[0]
        sock.close()
    except socket.error:
        pass
    return addr


class Path(object):
    @staticmethod
    def convert(path):
        if sys.platform == 'win32':
            path = path.replace("/", "\\")
        elif sys.platform.startswith('linux'):
            path = path.replace("\\", "/")
        else:
            pass
        return path


def delenv(name):
    logger.info("unset env: %s", name)
    if name in os.environ:
        del os.environ[name]
        
    if sys.platform == 'win32':
        ret = run("wmic ENVIRONMENT where \"name='%s'\" get UserName,VariableValue" % name)
        if "No Instance(s) Available" not in ret[1]:
            runex("wmic ENVIRONMENT where \"name='%s'\" delete" % name)
    elif sys.platform.startswith('linux'):
        runex("unset -v %s" % name )
        txtedit = Text.TextEditor("/etc/profile")
        txtedit.delete(r'^%s=' % name)
        txtedit.delete(r'^export %s' % name)
        txtedit.save()
    else:
        pass


def setenv(name, value):
    logger.info("set env: %s=%s", name, value)
    if sys.platform == 'win32':
        ret = run("wmic ENVIRONMENT where \"name='%s'\" get UserName,VariableValue" % name)
        if "No Instance(s) Available" in ret[1]:
            runex('wmic ENVIRONMENT create Name="%s",UserName="<system>",VariableValue="%s"' % (name, value))       
        else:
            runex("wmic ENVIRONMENT where \"name='%s' and username='<system>'\" set VariableValue=\"%s\"" % (name, value))
        runex("set %s=%s" % (name, value) )
    elif sys.platform.startswith('linux'):
        runex("export %s=%s" % (name, value) )
        txtedit = Text.TextEditor("/etc/profile")
        txtedit.set_param(name, value)
        txtedit.delete("export %s" % name)
        txtedit.insert("export %s" % name)
        txtedit.save()
    else:
        pass
    os.environ[name]=value


class Env(object):
    class Path(object):
        def __init__(self, name=None):
            self.__name = None
            self.__path = None
            if name:
                self.load(name)
        
        def load(self, name):
            self.__name = name
            self.__path = os.environ[name]
            logger.debug("get env: %s=%s", self.__name, self.__path)
    
        def append(self, segment):
            logger.debug("append %s into [%s]", segment, self.__name)
            #segment = Path.convert(segment)
            if self.__path.lower().find(segment.lower()) == -1:
                self.__path = "%s%s%s" % (self.__path, os.pathsep, segment)

        def delete(self, segment):
            logger.debug("delete %s in [%s]", segment, self.__name)
            #segment = Path.convert(segment)
            self.__path = self.__path.replace("%s%s" % (os.pathsep, segment), "")
        
        def replace(self, pattern, replace):
            logger.debug("replace: patter=[%s], replace=[%s]", pattern, replace)
            self.__path = re.sub(pattern, replace, self.__path)

        def uniqify(self):
            pass
        
        def contains(self, pattern):
            pass
        
        def save(self):
            setenv(self.__name, self.__path)

    @staticmethod
    def set(*args):
        setenv(*args)
    
    @staticmethod
    def unset(*args):
        delenv(*args)


class Service(object):
    STOPPED = 1
    UNKNOWN = 0
    RUNNING = 4
    
    def __init__(self, name, retry=1, interval=10):
        self.name = name
        self.retry = retry
        self.interval = interval
        
        if sys.platform == "win32":
            self._cmd_start = "sc start %s" % self.name
            self._cmd_stop = "sc stop %s" % self.name
            self._cmd_set_autostart = "sc config %s start= auto" % self.name
            self._cmd_unset_autostart = "sc config %s start= demand" % self.name
        elif sys.platform.startswith('linux'):
            self._cmd_start = "service %s start" % self.name
            self._cmd_stop = "service %s stop" % self.name
            self._cmd_set_autostart = "chkconfig %s on" % self.name
            self._cmd_unset_autostart = "chkconfig %s off" % self.name
        else:
            pass
        
    def status(self):
        status = self.UNKNOWN
        if sys.platform == "win32":
            (retcode, stdout) = run("sc query %s" % self.name)
            if "RUNNING" in stdout:
                status = self.RUNNING
            elif "STOPPED" in stdout or "not exist as" in stdout:
                status = self.STOPPED
            else:
                pass
        elif sys.platform.startswith('linux'):
            (retcode, stdout) = run("service %s status" % self.name)
            if retcode == 0:
                status = self.RUNNING
            else:
                if retcode == 1 or retcode ==3 or "stopped" in stdout or "unrecognized service" in stdout:
                    status = self.STOPPED
        else:
            pass
        return status

    def delete(self):
        self.stop()
        if sys.platform == "win32":
            run("sc delete %s" % self.name)
        elif sys.platform.startswith('linux'):
            svc_locate = "/etc/init.d/%s" % self.name
            if os.path.exists(svc_locate):
                File.remove(svc_locate)
            run("chkconfig --del" % self.name)
        else:
            pass
    
    def config(self, username=None, password=None, autostart=None):
        if username:
            runex("sc config %s obj= %s" % (self.name, username))
        if password:
            runex("sc config %s password= %s" % (self.name, password))
            
        if autostart is not None:
            if autostart:
                runex(self._cmd_set_autostart)
            else:
                runex(self._cmd_unset_autostart)
            
    def _op(self, operate, expected):
        redo = self.retry + 1
        while True:
            status = self.status()
            logger.debug("current status is %s, expected is %s, redo=[%s]", status, expected, redo)
                
            if status != expected:
                if redo > 0:
                    run(getattr(self, "_cmd_%s" % operate))
                    redo -= 1
                    time.sleep(self.interval)
                    continue
                else:
                    raise Exception("%s service %s failed" % (operate, self.name) )
            else:
                logger.debug("current status same with expected status. %s service %s successfully", operate, self.name)
                break

    def start(self):
        self._op("start", self.RUNNING)
    
    def stop(self):
        try:
            self._op("stop", self.STOPPED)
        except Exception:
            logger.warn("failed to stop the service %s. kill the process directly.", self.name)
            if sys.platform == "win32":
                queryex = run("sc queryex %s" % self.name)[1]
                match = re.search(r"PID[ \t]*:[ \t]*(\d+)", queryex)
                pid = match.group(1)
                runex("tskill %s" % pid)
            elif sys.platform.startswith('linux'):
                runex("killall %s" % self.name)
            else:
                pass
            #os.kill(pid, signal.SIGTERM)
    
    def restart(self):
        self.stop()
        self.start()


class Hosts(object):
    @staticmethod
    def locate():
        if sys.platform == 'win32':
            return os.path.join(os.environ["WINDIR"], 'system32\drivers\etc\hosts')
        elif sys.platform.startswith('linux'):
            return '/etc/hosts'
        else:
            pass

    @staticmethod
    def set(name, addr, filename=None):
        filename = filename or Hosts.locate()
        txt = Text.TextEditor(filename)
        txt.set_param(name, addr, "%(value)s  %(name)s")
        txt.save()
    
    @staticmethod
    def delete(name, filename=None):
        filename = filename or Hosts.locate()
        txt = Text.TextEditor(filename)
        txt.delete(name)
        txt.save()

    @staticmethod
    def dict(self, filename=None):
        filename = filename or Hosts.locate()
        pass
    
if __name__=="__main__":
    logging.basicConfig(
        level = logging.INFO, 
        format= '%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
