#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import re
import sys


class Validator(object):
    def __init__(self, pattern):
        self.pattern = pattern
    
    def validate(self, value):
        return re.search(self.pattern, value)


class IPv4Validator(Validator):
    def __init__(self):
        pattern = r'^([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])$'
        Validator.__init__(self, pattern)
        

class HostnameValidator(Validator):
    def __init__(self):
        pattern = r'^(?!\d)[a-zA-Z0-9-]{1,15}$'
        Validator.__init__(self, pattern)


class DirPathValidator(Validator):
    def __init__(self):
        if sys.platform == 'win32':
            pattern = r'^[a-zA-Z]:\\[ \w\\]*$'
        elif sys.platform.startswith('linux'):
            pattern = r'^(/)?([^/\0]+(/)?)+$'
        else:
            raise
        Validator.__init__(self, pattern)


class InteractiveInput(object):    
    def __init__(self):
        self._input = None
        major = sys.version_info[0]
        if major == 2:
            self._input = raw_input
        elif major == 3:
            self._input = input
        else:
            raise

    @staticmethod
    def message(text, style="DESCRIPTION"):
        if style == "TITLE":
            print("=" * len(text))
            print(text.upper())
            print("=" * len(text))
        elif style == "SECTION":
            print("\n*** %s ***" % text)
        else:
            print("\n%s" % text)

    def input(self, question, default=None, validation=None, regex=None):
        while True:
            try:
                if default:
                    value = self._input("\n%s[%s]:" % (question, default))
                else:
                    value = self._input("\n%s:" % question)
            except KeyboardInterrupt:
                print("\nQuit.")
                sys.exit(0)

            value = value or default
            if not value:
                continue
                          
            if validation:
                if validation == "IPV4":
                    regex = r'^([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])$'
                elif validation == "HOSTNAME":
                    regex = r'^(?!\d)[a-zA-Z0-9-]{1,15}$'
                elif validation == "DIRPATH":
                    if sys.platform == 'win32':
                        regex = r'^[a-zA-Z]:\\[ \w\\]*$'
                    elif sys.platform.startswith('linux'):
                        regex = r'^(/)?([^/\0]+(/)?)+$'
                    else:
                        pass

            if regex:
                if re.search(regex, value):
                    pass
                else:
                    print("ERROR! Please try again.\n")
                    continue
            return value

    def __TODO_input(self, question, default=None, validator=None):
        while True:
            try:
                if default:
                    value = self._input("\n%s[%s]:" % (question, default))
                else:
                    value = self._input("\n%s:" % question)
            except KeyboardInterrupt:
                print("\nQuit.")
                sys.exit(0)

            value = value or default
            if not value:
                continue

            if validator:
                if validator.validate(value):
                    pass
                else:
                    print("ERROR! Please try again.\n")
                    continue
            return value

    def select(self, question, choices, default=None):
        while True:
            print("\n%s" % question)
            for index in range(len(choices)):
                optkey = index + 1
                optval = choices[index]
                spacecount = len(str(len(choices))) - len(str(optkey))
                if default and default == optval:
                    line = "  %s%s) [%s]" % (" " * spacecount, " " * len(str(optkey)), optval)
                else:
                    line = "  %s%s) %s" % (" " * spacecount, optkey, optval)
                print(line)
                
            choice = self._input("Choice:")                
            if choice:
                if filter(lambda x: str(x) == choice, range(1, len(choices) + 1)):
                    value = choices[int(choice) - 1]
                else:
                    print("That's not one of the available choices. Please try again\n")
                    continue                    
            else:
                if default and filter(lambda x: x == default, choices):
                    value = default
                else:                    
                    print("That's not one of the available choices. Please try again\n")
                    continue
            return value

    @staticmethod
    def table(headers, contents):
        column_sizes = []
        for _ in range(len(headers)):
            size = len(headers[i])
            for row in contents:
                if len(row[i]) > size:
                    size = len(row[i])
            column_sizes.append(size)
    
        # Line 1, 3 and n: delimiters
        delimline = "+"
        for size in column_sizes:
            delimline += "-" * size + "+"
        print(delimline)
    
        # Line 2: column names
        nameline = "|"
        for _ in range(len(headers)):
            nameline += headers[i] + " " * (column_sizes[i] - len(headers[i])) + "|"
        print(nameline)
    
        print(delimline)
    
        for content in contents:
            contentline = "|"
            for _ in range(len(headers)):
                contentline += content[i] + " " * (column_sizes[i] - len(content[i])) + "|"
            print(contentline)
        print(delimline)
        
if __name__ == "__main__":
    i = InteractiveInput()
    ret = i.input("test")
    print(type(ret))