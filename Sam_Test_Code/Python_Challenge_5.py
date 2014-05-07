#!/usr/bin/python
# -*- coding: utf-8 -*-

import pickle
import urllib
import re

url = "http://www.pythonchallenge.com/pc/def/"
page = "peak.html"
sock = urllib.urlopen(url + page)
source = sock.read()
sock.close()

R = re.compile("<peakhell src=\"(.*)\"")

page = re.search(R, source)
#print page.group(1)
sock = urllib.urlopen(url + page.group(1))
data = sock.read()
sock.close()

number_list = pickle.loads(data)
print number_list

string = ""
for line in number_list:
    for yuan in line:
        string += yuan[0]*yuan[1]
    string += "\n"

print string


