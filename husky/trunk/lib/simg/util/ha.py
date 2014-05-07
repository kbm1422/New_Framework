#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import re
import time


import simg.io.text as Text
import simg.io.file as File
import simg.os as OS
import simg.util.zip as Zip


class Drbd(object):
    def __init__(self, resources, machines):
        self.resources = resources
        self.machines  = machines
        
        self._svc   = OS.Service("drbd")
        self._txt   = Text.TextEditor()

    def initialize(self):
        pass
  
    def backup(self, dst):
        def bak(disk, dirpath, dst):
            File.mkpath(dirpath)
            OS.linux.mount(disk, dirpath, "ext4")
            File.copy(dirpath, "%s.cache" % dirpath)
            
            zipfile = "%s%s.zip" % (dst, dirpath)
            if os.path.exists(zip):
                logger.debug("backup zip file '%s' exist, skip to backup", zipfile)
            else:
                logger.debug("backup zip file '%s' not exist, do the backup", zipfile)
                Zip.archive("%s.cache" % dirpath, zip)

        bak(self.resources["r0"]["disk"], self.resources["r0"]["dir"], dst)
        bak(self.resources["r1"]["disk"], self.resources["r1"]["dir"], dst)      

    
    def install(self, src_dir):
        self.stop()
        OS.linux.Rpm("drbd84-utils").install(src_dir)
        OS.linux.Rpm("kmod-drbd84").install(src_dir)
    
    
    def config(self):
        logger.debug("*** Generate /etc/drbd.conf.")
        drbdconf = """
global {
usage-count no;
}

resource r0 {
protocol C;
#incon-degr-cmd "echo !DRBD! pri on incon-degr | wall ; sleep 60 ; halt -f";

on %(m0_hostname)s {
device     %(r0_device)s;
disk       %(r0_disk)s;
address    %(m0_linkip)s:7789;
meta-disk  internal;
}
on %(m1_hostname)s {
device     %(r0_device)s;
disk       %(r0_disk)s;
address    %(m1_linkip)s:7789;
meta-disk  internal;
}

disk {
on-io-error   detach;
}

net {
max-buffers     2048;
ko-count 4;
}

syncer {
rate 25M;
al-extents 257; # must be a prime number
}

startup {
wfc-timeout  20;
degr-wfc-timeout 120;    # 2 minutes.
}
}

resource r1 {
protocol C;
#incon-degr-cmd "echo !DRBD! pri on incon-degr | wall ; sleep 60 ; halt -f";

on %(m0_hostname)s {
device     %(r1_device)s;
disk       %(r1_disk)s;
address    %(m0_linkip)s:7790;
meta-disk  internal;
}
on %(m1_hostname)s {
device     %(r1_device)s;
disk       %(r1_disk)s;
address    %(m1_linkip)s:7790;
meta-disk  internal;
}

disk {
on-io-error   detach;
}

net {
max-buffers     2048;
ko-count 4;
}

syncer {
rate 25M;
al-extents 257; # must be a prime number
}

startup {
wfc-timeout  20;
degr-wfc-timeout 120;    # 2 minutes.
}
}
        """ % { "m0_hostname":  self.machines["m0"]["hostname"], 
                "m1_hostname":  self.machines["m1"]["hostname"], 
                "r0_device":    self.resources["r0"]["device"], 
                "r1_device":    self.resources["r1"]["device"], 
                "r0_disk":      self.resources["r0"]["disk"], 
                "r1_disk":      self.resources["r1"]["disk"], 
                "m0_linkip":    self.machines["m0"]["linkip"], 
                "m1_linkip":    self.machines["m1"]["linkip"], 
               }

        logger.debug("/etc/drbd.conf: %s" % drbdconf)
        self._txt.load(text=drbdconf)
        self._txt.save("/etc/drbd.conf")
    
        logger.debug("*** Initialize disk partitions.")
        OS.linux.umount( self.resources["r0"]["disk"] )
        OS.linux.umount( self.resources["r1"]["disk"] )
        OS.runex("dd if=/dev/zero bs=1M count=1 of=%s" % self.resources["r0"]["disk"])
        OS.runex("dd if=/dev/zero bs=1M count=1 of=%s" % self.resources["r1"]["disk"])
        
        logger.debug("*** Create Resources.")
        
        OS.runex("yes yes | drbdadm create-md r0")
        OS.runex("yes yes | drbdadm create-md r1")

    
    def startup(self, instance):
        nic = self.machines["m%s" % instance]["nic"]    
        self._txt.load(file="/etc/sysconfig/network-scripts/ifcfg-%s" % nic)
        self._txt.set_param("BOOTPROTO", "static")
        self._txt.set_param("DHCPCLASS", "")
        self._txt.set_param("IPADDR", self.machines["m%s" % instance]["linkip"])
        self._txt.set_param("NETMASK", "255.255.255.0")
        self._txt.set_param("ONBOOT", "yes")
        self._txt.save()
        
        logger.debug("restart the network interface")
        OS.runex("ifdown %s" % nic)
        OS.runex("ifup %s" % nic)
        
        self._svc.start()
        if not os.path.exists("/proc/drbd"):
            raise Exception("ERROR: cannot start drbd service.")

        drbd_status = None
        
        logger.debug("*** active resources.")
        if instance == 0 :
            drbd_status = ".*Primary.*UpToDate.*"
            logger.debug("r0, r1 are set as primary.")
            OS.runex("drbdadm -- --overwrite-data-of-peer primary r0")
            OS.runex("drbdadm -- --overwrite-data-of-peer primary r1")
        elif instance == 1:
            drbd_status = ".*Secondary.*UpToDate/UpToDate.*"
            logger.debug("r0, r1 are set as secondary.")
            OS.runex("drbdadm secondary r0")
            OS.runex("drbdadm secondary r1")
            
            step_pass = False
            
            logger.debug("*** Waiting for secondary drbd resources to sync")
            logger.debug("*** It will take half an hour or more depends on the disk size.")
    
            while not step_pass:
                self._txt.load(file="/proc/drbd")
                proc_drbd = self._txt.read()
                logger.debug("/proc/drbd: \n%s", proc_drbd)
                if "sync'ed" not in proc_drbd:
                    step_pass = True
                time.sleep(30)
        else:
            raise Exception("instance must be 0 or 1")

        logger.debug("*** Waiting for drbd resources ready")
        drbd_r0_status = 0
        drbd_r1_status = 0
        while drbd_r0_status != 1 or drbd_r1_status != 1: 
            self._txt.load(file="/proc/drbd")
            proc_drbd = self._txt.read()
            logger.debug("/proc/drbd: \n%s", proc_drbd)
            if re.search("0:%s" % drbd_status, proc_drbd):
                drbd_r0_status = 1
            
            if re.search("1:%s" % drbd_status, proc_drbd):
                drbd_r1_status = 1
            time.sleep(10)

        logger.debug("*** Resources are ready.")
        self._txt.load(file="/proc/drbd")
        proc_drbd = self._txt.read()
        logger.debug("/proc/drbd: \n%s", proc_drbd)
        
        if instance == 0:
            logger.debug("*** Format DRBD devices.")
            OS.runex("mkfs.ext4 %s" % self.resources["r0"]["device"])
            OS.runex("mkfs.ext4 %s" % self.resources["r1"]["device"])
            OS.linux.mount( self.resources["r0"]["device"], self.resources["r0"]["dir"], "ext4" )
            OS.linux.mount( self.resources["r1"]["device"], self.resources["r1"]["dir"], "ext4" )
            (retcode, svc_status) = OS.run("service drbd status")
            if retcode != 0:
                raise Exception("get drbd service status failed")
            if re.search("0:r0%s%s" % (drbd_status, self.resources["r0"]["dir"]), svc_status) and re.search("1:r1%s%s" % (drbd_status, self.resources["r1"]["dir"]), svc_status):
                logger.debug("drbd installation successfully.")
            else:
                raise Exception("drbd installation failed.")
                
            File.move( "%s.cache" % self.resources["r0"]["dir"], self.resources["r0"]["dir"] )
            File.move( "%s.cache" % self.resources["r1"]["dir"], self.resources["r1"]["dir"] )
    
        self._svc.config(autostart=True)
        self._txt.load(file="/etc/fstab")
        self._txt.delete(r"%s|%s" % (self.resources["r0"]["disk"], self.resources["r1"]["dir"]))
        self._txt.save()
        logger.debug("*** DRBD Setup Finished.")

    def uninstall(self):
        self.stop()
        OS.linux.Rpm("kmod-drbd84").uninstall()
        OS.linux.Rpm("drbd84-utils").uninstall()
        if os.path.exists("/etc/drbd.conf"):
            File.remove("/etc/drbd.conf")

    def stop(self):
        for svcname in self.resources["r0"]["services"]:
            OS.Service(svcname).stop()
        for svcname in self.resources["r1"]["services"]:
            OS.Service(svcname).stop()

        OS.linux.umount( self.resources["r0"]["dir"] )
        OS.linux.umount( self.resources["r1"]["dir"] )
    
        while os.path.exists("/proc/drbd"):
            logger.warn("drbd is running. Try to stop it.")
            self._svc.stop()


class Heartbeat(object):
    def __init__(self, resources, machines):
        self.resources = resources
        self.machines  = machines
        
        self._svc   = OS.Service("heartbeat")
        self._txt   = Text.TextEditor()
    
    def install(self, src_dir):
        OS.linux.Rpm("perl-TimeDate").install(src_dir)
        OS.linux.Rpm("PyXML").install(src_dir)
        OS.linux.Rpm("cluster-glue-libs").install(src_dir)
        OS.linux.Rpm("cluster-glue", ver="1.0.5-6").install(src_dir)
        OS.linux.Rpm("resource-agents").install(src_dir)
        OS.linux.Rpm("heartbeat-libs").install(src_dir, nodeps=True)
        OS.linux.Rpm("heartbeat", ver="3.0.4-1").install(src_dir)

    def startup(self, instance):
        authkeys = """auth 1
1 sha1 heartbeat
"""
        self._txt.load(text=authkeys)
        self._txt.save("/etc/ha.d/authkeys")
        File.chmod("/etc/ha.d/authkeys", 0o600)
        
        peer_nic = None
        peer_linkip = None
        
        if instance == 0:
            peer_nic = self.machines["m1"]["nic"]
            peer_linkip  = self.machines["m1"]["linkip"]
        elif instance == 1:
            peer_nic = self.machines["m0"]["nic"]
            peer_linkip  = self.machines["m0"]["linkip"]
        else:
            raise Exception("instance must be 0 or 1")
        
        ha_cf = """logfile /var/log/hb.log
debugfile /var/log/heartbeat-debug.log
keepalive 1
warntime 10
deadtime 30
initdead 120
udpport 694
ucast %(peer_nic)s %(peer_linkip)s

auto_failback on
node %(m0_hostname)s
node %(m1_hostname)s
crm no
""" % { "m0_hostname":  self.machines["m0"]["hostname"], 
        "m1_hostname":  self.machines["m1"]["hostname"], 
        "peer_nic":     peer_nic,
        "peer_linkip":  peer_linkip,
      }
        self._txt.load(text=ha_cf)
        self._txt.save("/etc/ha.d/ha.cf")


        haresources = """%(m0_hostname)s  IPaddr::%(r0_virtual_addr)s/%(r0_virtual_cidr)s/%(r0_virtual_nic)s drbddisk::r0 Filesystem::%(r0_device)s::%(r0_dir)s::ext4 %(r0_services)s
%(m1_hostname)s  IPaddr::%(r1_virtual_addr)s/%(r1_virtual_cidr)s/%(r1_virtual_nic)s drbddisk::r1 Filesystem::%(r1_device)s::%(r1_dir)s::ext4 %(r1_services)s
""" % { "m0_hostname":          self.machines["m0"]["hostname"],
        "r0_virtual_nic":       self.resources["r0"]["virtual_ip"][0]["nic"],
        "r0_virtual_cidr":      self.resources["r0"]["virtual_ip"][0]["cidr"],
        "r0_virtual_addr":      self.resources["r0"]["virtual_ip"][0]["addr"],
        "r0_device":            self.resources["r0"]["device"],
        "r0_dir":               self.resources["r0"]["dir"],
        "r0_services":          " ".join(self.resources["r0"]["services"]) if self.resources["r0"]["services"] else "",
        
        "m1_hostname":          self.machines["m1"]["hostname"],
        "r1_virtual_nic":       self.resources["r1"]["virtual_ip"][0]["nic"],
        "r1_virtual_cidr":      self.resources["r1"]["virtual_ip"][0]["cidr"],
        "r1_virtual_addr":      self.resources["r1"]["virtual_ip"][0]["addr"],
        "r1_device":            self.resources["r1"]["device"],
        "r1_dir":               self.resources["r1"]["dir"],
        "r1_services":          " ".join(self.resources["r1"]["services"]) if self.resources["r1"]["services"] else "",
      }
        self._txt.load(text=haresources)
        self._txt.save("/etc/ha.d/haresources")
        
        self._svc.start()


    def uninstall(self):
        self.stop()
        OS.linux.Rpm("perl-TimeDate").uninstall()
        OS.linux.Rpm("PyXML").uninstall()
        OS.linux.Rpm("cluster-glue-libs").uninstall()
        OS.linux.Rpm("cluster-glue").uninstall()
        OS.linux.Rpm("resource-agents").uninstall()
        OS.linux.Rpm("heartbeat-libs").uninstall()
        OS.linux.Rpm("heartbeat").uninstall()
        if os.path.exists("/etc/ha.d"):
            File.remove("/etc/ha.d")    

    def stop(self):
        for svcname in self.resources["r0"]["services"]:
            OS.Service(svcname).stop()
        for svcname in self.resources["r1"]["services"]:
            OS.Service(svcname).stop()
        self._svc.stop()


if __name__=="__main__":
    logging.basicConfig(
        level = logging.DEBUG, 
        format= '%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
    resources = {
        "r0": {
                "device": "/dev/drbd0", 
                "disk"  : "/dev/sdb1", 
                "dir"   : "/drbd0", 
                "virtual_ip": [
                    { "nic": "eth0", "addr": "172.30.66.221", "host": "ADMIN1-SS-CL", "cidr": "24" },
                ], 
                "services": []
            },
        "r1": {
                "device": "/dev/drbd1", 
                "disk"  : "/dev/sda3", 
                "dir"   : "/drbd1", 
                "virtual_ip": [
                    {"nic": "eth0", "addr": "172.30.66.223", "host": "ADMIN2-SS-CL", "cidr": "24"},
                ], 
                "services": [] 
            },
    }
    machines = {
        "m0": { "hostname": "ha1", "linkip": "10.30.66.221", "nic": "eth1" },
        "m1": { "hostname": "ha2", "linkip": "10.30.66.223", "nic": "eth1" },        
    }
    
    drbd = Drbd(resources, machines)
    drbd.backup("/xormedia/backup")
    drbd.install("/xormedia/drbd")
    drbd.config()
    drbd.startup(1)

#     heartbeat = Heartbeat()
#     heartbeat.install("/xormedia/heartbeat")