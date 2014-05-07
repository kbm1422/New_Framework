#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import sys

messages = ["this is the message",
            "It will be sent",
            "in parts"]

class SocketClient(object):

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.buffer_size = 4096
        self.socks = []

    def client_setup(self):
        for i in range(10):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socks.append(sock)
        for s in self.socks:
            s.connect((self.ip_address, self.port))
        for message in messages:
            counter = 1
            for s in self.socks:
                print "%s sending %s" % (counter, message)
                s.send(message)
                counter += 1
            for s in self.socks:
                data = s.recv(self.buffer_size)
                print "Received %s" % data
                if not data:
                    print "closing socket %s" % s.getpeername()
                    s.close()

if __name__ == "__main__":

    myClient = SocketClient("172.16.132.85", 40000)
    myClient.client_setup()
