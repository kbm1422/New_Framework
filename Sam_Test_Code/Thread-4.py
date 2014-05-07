__author__ = 'ywu'

import threading
import Queue

queue = Queue.Queue()
queue.put("1")
queue.put("2")


class myThread(threading.Thread):

    def __init__(self,thread_name,queue):
        threading.Thread.__init__(self, name=thread_name)
        self.queue = queue

    def run(self):
        while True:
            print "%s is get %s" % (self.getName(),self.queue.get())
            self.queue.task_done()
            print "lll"
            print queue.empty()

def main():

    t = myThread("sam",queue)
    t.setDaemon(True)
    t.start()
    queue.join()


if __name__ == "__main__":

    main()







