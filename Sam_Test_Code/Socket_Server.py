#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import select
import Queue


class SocketServer(object):

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.buffer_size = 4096
        self.timeout = 10

    def server_setup(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip_address, self.port))
        sock.listen(5)
        rlists = [sock]
        wlists = []
        elists = []
        meg_queue = {}
        while rlists:
            rs, ws, es = select.select(rlists, wlists, elists, self.timeout)
            if not (rs or ws or es):
                print "timeout....no message"

            for s in rs:
                if s is sock:
                    client_sock, client_addr = sock.accept()
                    print "%s: connected" % client_addr[1]
                    client_sock.setblocking(False)
                    rlists.append(client_sock)
                    meg_queue[client_sock] = Queue.Queue()
                else:
                    data = s.recv(self.buffer_size)
                    if data:
                        print data
                        meg_queue[s].put("I receive your message:" + data)
                        if s not in wlists:
                            wlists.append(s)
                    else:
                        if s in wlists:
                            wlists.remove(s)
                        rlists.remove(s)
                        s.close()
                        del meg_queue[s]

            for s in ws:
                try:
                    next_msg = meg_queue[s].get_nowait()
                except Queue.Empty:
                    print "%s: Message Queue is empty, remove socket" % s.getpeername()[1]
                    wlists.remove(s)
                else:
                    print "%s Sending: %s" % (s.getpeername()[1], next_msg)
                    s.send(next_msg)

            for s in es:
                print "exception on %s" % s.getpeername()
                rlists.remove(s)
                if s in wlists:
                    wlists.remove(s)
                s.close()
                del meg_queue[s]

if __name__ == "__main__":

    MySocket = SocketServer("172.16.132.85", 40000)
    MySocket.server_setup()



