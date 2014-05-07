#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import libxml2

class SimpleXPathEditor(object):
    def __init__(self, filename=None, xmlstring=None):
        if filename or xmlstring:
            self.load(filename, xmlstring)

    def find(self, xpath):
        if self.exists(xpath):
            nodes = []
            for node in self._xpc.xpathEval(xpath):
                nodes.append(node)
                #yield node
            return nodes
        else:
            raise Exception("Fail to find nodes by xpath: %s" % xpath)

    def reg_namesapce(self, prefix, uri):
        self._xpc.xpathRegisterNs(prefix, uri)

    def exists(self, xpath):
        return True if self._xpc.xpathEval(xpath) else False

    def load(self, filename=None, xmlstring=None):
        if xmlstring:
            if filename:
                raise Exception("can't specify param 'filename' and 'xmlstring' at the same time")
            else:
                self._doc = libxml2.parseDoc(xmlstring)
        elif filename:
            logger.info("load xml: %s", filename)
            self._filename = filename
            self._doc = libxml2.parseFile(filename)
            #self._doc = libxml2.readFile(filename, encoding=None, options=libxml2.XML_PARSE_NOBLANKS)  #XML_PARSE_NOBLANKS XML_DTD_NO_DTD
        else:
            raise Exception("'filename' or 'xmlstring' is required as an alternative param")
        
        self._xpc = self._doc.xpathNewContext()
        logger.log( logging.NOTSET, "load xml string: \n%s", self._doc )


    def save(self, filename=None):
        tofile = os.path.realpath(filename) if filename else self._filename
        logger.info("save xml: %s", tofile)
        savedoc = libxml2.readDoc(self._doc.serialize(), URL=None, encoding=None, options=libxml2.XML_PARSE_NOBLANKS)
        savedoc.saveFormatFile(tofile, format=1) 
        #libxml2.keepBlanksDefault(False)
        #self._doc.saveFormatFile(tofile, format=1) 
        logger.log( logging.NOTSET, "save xml string: \n%s", savedoc.serialize(format=1) )
        self._xpc.xpathFreeContext()
        self._doc.freeDoc()


    def insert(self, xpath, text, position="under", key=None, overwrite=True):
        """
        @param position: 
            unique: xpath specify the unique node
            under : insert node under xpath, we can use key to specify the unique
            before: insert node before xpath, we can use key to specify the unique
            after : insert node after xpath, we can use key to specify the unique
        @bug: when position is before or after,
              if the node indicated by xpath and the node indicated by key with same parent node,
              and the xpath doesn't specify the unique node in parent node, it will raise Exception
        """
        logger.info("insert: xpath=%s, key=%s, overwrite=%s, position=%s, text=%s" , xpath, key, overwrite, position, text)

        self.POSITION_UNIQUE = "unique"
        self.POSITION_UNDER  = "under"
        self.POSITION_BEFORE = "before"
        self.POSITION_AFTER  = "after"
        
        insert_node = libxml2.parseDoc(text).getRootElement()
        if position == self.POSITION_UNDER:            
            def __addNode(ref_node=None):
                for node in self.find(xpath):
                    node.addChild(insert_node.copyNode(1)) 
            
            if key:
                insert_node_xapth = "%s/%s" % (xpath,key)
                if self.exists(insert_node_xapth):
                    if overwrite:
                        self.delete(insert_node_xapth)
                        __addNode()
                else:
                    __addNode()
            else:
                __addNode()
        elif position == self.POSITION_UNIQUE:
            tup = xpath.rpartition("/")
            self.insert(tup[0], text, self.POSITION_UNDER, tup[2], overwrite)
        else:
            def __addSiblingNode(ref_node):
                if position == self.POSITION_BEFORE:
                    ref_node.addPrevSibling(insert_node.copyNode(1))
                elif position == self.POSITION_AFTER:
                    ref_node.addNextSibling(insert_node.copyNode(1))
                else:
                    pass
            
            for ref_node in self.find(xpath):
                if key:
                    parent_node_xpath = ref_node.parent.nodePath()
                    insert_node_xapth = "%s/%s" % (parent_node_xpath,key)
                    if self.exists(insert_node_xapth):
                        if overwrite:
                            self.delete(insert_node_xapth)
                            __addSiblingNode(ref_node)
                            #ref_node.unlinkNode()
                    else:
                        __addSiblingNode(ref_node)
                else:            
                    __addSiblingNode(ref_node)
  

    def delete(self, xpath):
        logger.info("delete: xpath=%s", xpath)
        if self.exists(xpath):
            for node in self.find(xpath):
                node.unlinkNode()
        else:
            logger.info("delete: %s not exist, do nothing.", xpath)
       
        
    def set_attr(self, xpath, value):
        logger.info("set_attr: xpath=%s, value=%s", xpath, value)
        if self.exists(xpath):
            for node in self.find(xpath):
                node.setContent(value)
        else:
            tup = xpath.rpartition("/")
            if tup[2].find("@", 0, 1) == 0:
                name = tup[2].strip("@")
                parent_xpath = tup[0]
                for node in self.find(parent_xpath):
                    node.setProp(name, value)
            else:
                raise Exception("invalid xpath when set attribute: %s" % xpath)
    
    def set_text(self, xpath, text):
        logger.info("set_text: xpath=%s, text=%s", xpath, text)
        if self.exists(xpath):
            for node in self.find(xpath):
                node.setContent(text)
        else:
            tup = xpath.rpartition("/")
            if tup[2] == "text()":
                parent_xpath = tup[0]
            else:
                parent_xpath = xpath            
            for node in self.find(parent_xpath):
                node.setContent(text)

    def set_value(self, xpath, value):
        logger.info("set_value: xpath=%s, value=%s", xpath, value)
        for node in self.find(xpath):
            node.setContent(value)

    def get_value(self, xpath):
        logger.info("get_value: xpath=%s", xpath)
        ret = []
        for node in self.find(xpath):
            ret.append(node.getContent())
        return ret
        
    def copy(self, xpath, from_file=None, from_xpath=None, new_name=None, overwrite=None):
        from_file = from_file or self._filename
        overwrite = overwrite if overwrite else 0 if from_xpath else 1

        logger.info("copy: xpath=%s, from_file=%s, from_xpath=%s, new_name=%s, overwrite=%s", xpath, from_file, from_xpath, new_name, overwrite)
        
        xml = self.__class__(file=from_file)
        if from_xpath:
            from_node_list = xml.find(from_xpath)
            to_node_list = self.find(xpath)
            for to_node in to_node_list:
                for child_node in to_node.children:
                    if overwrite:
                        remove_child_node_name = new_name if new_name else from_node_list[0].name
                        if child_node.name == remove_child_node_name:
                            child_node.unlinkNode()
                            
                for from_node in from_node_list:
                    if new_name:
                        from_node.setName(new_name)
                    to_node.addChild(from_node.copyNode(1))
        else:
            from_node_list = xml.find(xpath)
            if self.exists(xpath) and overwrite:
                node_list = self.find(xpath)
                for node in node_list:
                    if node.name == from_node_list[0].name:
                        node.unlinkNode()
        
            for from_node in from_node_list:
                parent_node_xpath = from_node.parent.nodePath()
                parent_node_list  = self.find(parent_node_xpath)
                for parent_node in parent_node_list:
                    parent_node.addChild(from_node.copyNode(1))
