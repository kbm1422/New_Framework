__author__ = 'ywu'

import threading
import datetime
import time


class ThreadTime(threading.Thread):

    def run(self):
        time = datetime.datetime.now()
        print "%s: say hello at time: %s" % (self.getName(),time)

if __name__ == "__main__":

    for i in range(10):
        t = ThreadTime()
        time.sleep(1)
        t.start()
