#!/usr/bin/python
# -*- coding: utf-8 -*-

import string
import re
import urllib

sock = urllib.urlopen("http://www.pythonchallenge.com/pc/def/equality.html")
source = sock.read()
sock.close()

R = re.compile("<!--(.+?)-->", re.DOTALL)
data = re.findall(R, source)

E = re.compile("[^A-Z][A-Z]{3}([a-z])[A-Z]{3}[^A-Z]")
word = re.findall(E, data[0])

print "".join(word)



