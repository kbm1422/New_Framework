#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from xml.dom import minidom

class Element(minidom.Element):
    def addSubElement(self, tagName, position=None, refChild=None):
        subelement = self.ownerDocument.createElement(tagName)
        if position == "before":
            self.insertBefore(subelement, refChild)
        elif position == "after":
            newRefChild = refChild.nextSibling
            self.insertBefore(subelement, newRefChild)
        else:
            self.appendChild(subelement)
        return subelement
    
    def addTextNode(self, data):
        textnode = self.ownerDocument.createTextNode(data)
        self.appendChild(textnode)
        return textnode
    
    def addAttribute(self, name, value):
        attr = self.ownerDocument.createAttribute(name)
        attr.value = value
        self.setAttributeNode(attr)
        return attr

#override original Element class
minidom.Element = Element

if __name__ == "__main__":
    pass