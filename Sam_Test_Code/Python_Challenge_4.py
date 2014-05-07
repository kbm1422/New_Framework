#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import re

url = "http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing="
number = "12345"

R = re.compile("(\d+)$")
D = re.compile("Divide")

while True:
    source = urllib.urlopen(url + number).read()
    match = re.search(R, source)
    divide = re.search(D, source)
    if match:
        number = match.group()
        print number
    elif divide:
        number = str(int(number) / 2)
    else:
        break

#print "the url is: %s" % url + str(int(number) / 2)
print source
