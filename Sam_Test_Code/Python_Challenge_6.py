#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib
import sys
import zipfile
import re

zip_file = sys.path[0] + "/channel.zip"

url = "http://www.pythonchallenge.com/pc/def/channel.zip"


def download_zip_file():
    try:
        urllib.urlretrieve(url, path)
    except:
        print "Cannot get the file"

zf = zipfile.ZipFile(zip_file)
R = re.compile("(\d+)$")
nothing = "90052"
comments = []
while True:
    comments.append(zf.getinfo(nothing + ".txt").comment)
    temp = re.search(R, zf.read(nothing + ".txt"))
    if temp:
        nothing = temp.group()
        print nothing
    else:
        break

print "".join(comments)

