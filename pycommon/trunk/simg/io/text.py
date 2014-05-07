#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import re
import os

import simg.io.file as fs


class TextEditor(object):
    def __init__(self, filename=None, text=None):
        self.__filename = None
        self.__lines = []
        if filename or text:
            self.load(filename, text)
            
    def load(self, filename=None, text=None):
        if text:
            if filename:
                raise Exception("can't specify param 'file' and 'text' at the same time")
            else:
                logger.info("load: text=%s", text)
                self.__lines = text.splitlines(True)
        elif filename:
            logger.info("load: file=%s", filename)
            self.__filename = filename
            with open(filename, "r") as fsrc:
                self.__lines = fsrc.readlines()
        else:
            raise Exception("'file' or 'text' is required as an alternative param")

    def read(self):
        return "".join(self.__lines)

    def readlines(self):
        return self.__lines

    def save(self, filename=None):
        tofile = filename or self.__filename
        logger.info("save file: %s", tofile)
        if not os.path.exists(tofile):
            fs.touch(tofile)
        with open(tofile, 'w') as fdst:
            fdst.write("".join(self.__lines))
    
    def insert(self, text, linenum=None):
        logger.info("insert: linenum=%s, text=%s", linenum, text)
        text = str(text)+"\n"
        if linenum:
            self.__lines.insert(text, linenum-1)
        else:
            self.__lines.append(text)
       
    def delete(self, pattern):
        logger.info("delete: pattern=%s", pattern)
        self.__lines = filter(lambda line: not re.search(pattern, line), self.__lines)
    
    def search(self, pattern):
        logger.info("search: pattern=%s", pattern)
        return filter(lambda line: re.search(pattern, line), self.__lines)
    
    def replace(self, pattern, replace):
        logger.info("replace: pattern=%s, replace=%s", pattern, replace)
        self.__lines = map(lambda line: re.sub(pattern, replace, line), self.__lines)
    
    def set_param(self, name, value, style="%(name)s=%(value)s"):
        logger.info("set_param: name=%s, value=%s, style=%s", name, value, style)
        match = re.search('%\(name\)s(.*)%\(value\)s', style)
        if match:
            separator = match.group(1)
            pattern = r"%s[ \t]*%s.*" % (name, separator)
        else:
            match = re.search('%\(value\)s(.*)%\(name\)s', style)
            separator = match.group(1)
            pattern = r".*%s%s" % (separator, name)

        replace = style % {"name": name, "value": value}
        if self.search(pattern):
            self.replace(pattern, replace)
        else:
            self.insert(replace)

    def get_param(self, name, style="%(name)s=%(value)s"):
        match = re.search('%\(name\)s(.*)%\(value\)s', style)
        if match:
            separator = match.group(1)
            pattern = r"%s[ \t]*%s(.*)" % (name, separator)
        else:
            match = re.search('%\(value\)s(.*)%\(name\)s', style)
            separator = match.group(1)
            pattern = r"(.*).*%s%s" % (separator, name)
        lines = self.search(pattern)
        value = None
        if lines:
            for line in lines:
                if re.match(r"[ \t]#", line):
                    continue
                else:
                    match = re.search(pattern, line)
                    value = match.group(1)
                    break
        if value is not None:
            value = value.strip()
        return value
        
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
    txt = TextEditor(r"D:\Sync\Workspace\pytests\ba_driver_test.ini")
    value = txt.get_param("sink_swam3_logfile")
    print(value)