__author__ = 'ywu'

import string
a ="g fmnc wms bgblr rpylqjyrc gr zw fylb. rfyrq ufyr amknsrcpq ypc dmp. bmgle gr gl zw fylb gq glcddgagclr ylb rfyr'q ufw rfgq rcvr gq qm jmle. sqgle qrpgle.kyicrpylq() gq pcamkkclbcb. lmu ynnjw ml rfc spj."
#a ="http://www.pythonchallenge.com/pc/def/map.html"
b = ""
for c in a:
    if c in string.letters:
        rule = string.maketrans(c, chr((ord(c) + 2 - 97) % 26 + 97))
        b += string.translate(c, rule)
    else:
        b += c

print b
