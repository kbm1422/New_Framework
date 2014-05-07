#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)


def trimHexString(s):
    return hex(int(s, 16))


def trimMacAddress(addr):
    new = []
    addr = addr.strip()
    if ":" in addr:
        old = addr.split(":")
        for item in old:
            if len(item) == 1:
                item = "0" + item
            item = item.upper()
            new.append(item)
        return ":".join(new)
    else:
        return ':'.join(s.encode('hex').upper() for s in addr.decode('hex'))


def quote(s):
    logger.debug("string before quote: %s", s)
    bytelist = s.encode("ascii")
    ret = ""
    for asc in bytelist:
        ascint = int()
        if isinstance(asc, str):
            ascint = ord(asc)
        elif isinstance(asc, int):
            ascint = asc
        else:
            raise
        ascstr = chr(ascint)
        if ascstr in """!#$%&'()*+,/:;=?@[] "%-.<>\^_`{|}~""":
            ascstr = hex(ascint).replace("0x", "%").upper()
        ret += ascstr
    logger.debug("string after quote: %s", ret)
    return ret


def unquote(s):
    pass

if __name__ == "__main__":
    print trimMacAddress("0dd694ca4f00")
