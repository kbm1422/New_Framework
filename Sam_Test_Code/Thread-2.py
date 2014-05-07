__author__ = 'ywu'

import urllib2
import time


class ThreadUrl(object):
    hosts = ["http://www.google.com.hk","http://www.baidu.com","http://ibm.com"]
    start = time.time()
    for host in hosts:
        url = urllib2.urlopen(host)
        print url.read(1024)
    print "Time Took: %s" % (time.time()-start)