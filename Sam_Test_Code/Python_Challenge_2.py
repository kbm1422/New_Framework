#!/usr/bin/python
# -*- coding: utf-8 -*-

import string
import urllib2
import re


socket = urllib2.urlopen("http://www.pythonchallenge.com/pc/def/ocr.html")
source = socket.read()
socket.close()

R = re.compile(r"<!--(.*?)-->", re.S)
data = re.findall(R, source)

#best solution
b = filter(lambda x: x in string.ascii_lowercase, data[1])
print b

#my solution
# rule = string.maketrans("","")
# b = data[1].translate(rule,"!@#$%^&*()_+{}[]\n")
# print b
