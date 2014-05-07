#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import libxml2
import libxslt

class TransformerFactory(object):
    """
    See <Factory> design pattern for detail: http://www.oodesign.com/factory-pattern.html
    """
    @classmethod
    def netTransformer(self, styleFilename=None, styleXmlstring=None):
        if styleFilename:
            if styleXmlstring:
                raise ValueError("can't specify param 'styleFilename' and 'styleXmlstring' at the same time")
            else:
                return FileTransformer(styleFilename)
        elif styleXmlstring:
            return StreamTransformater(styleXmlstring)
        else:
            raise ValueError("'styleFilename' or 'styleXmlstring' is required as an alternative param")


from abc import ABCMeta, abstractmethod
class BaseTransformer(object):
    __metaclass__ = ABCMeta

    def __init__(self, styleSrc=None):
        """
        @param style: style should be xml filename or xml string
        """
        if styleSrc:
            self.load(styleSrc)

    @abstractmethod
    def load(self):
        pass

    def applyStylesheetOnFile(self, srcFilename):
        self._srcDoc = libxml2.parseFile(srcFilename)
        self._applyStylesheet()

    def applyStylesheetOnStream(self, srcXmlstring):
        self._srcDoc = libxml2.parseDoc(srcXmlstring)
        self._applyStylesheet()
    
    def _applyStylesheet(self):
        self._result = self._style.applyStylesheet(self._srcDoc, None)
        self._srcDoc.freeDoc()
    
    def saveResultToSring(self):
        self._style.saveResultToSring(self._result)
    
    def saveResultToFilename(self, dstFilename):
        self._style.saveResultToFilename(dstFilename, self._result, 0)

    def __del__(self):
        self._style.freeStylesheet()
        self._result.freeDoc()


class FileTransformer(BaseTransformer):
    def load(self, styleFilename):
        logger.info("load style xml filename: %s", styleFilename)
        self._styleDoc = libxml2.parseFile(styleFilename)
        self._style = libxslt.parseStylesheetDoc(self._styleDoc)
    
    
class StreamTransformater(BaseTransformer):
    def load(self, styleXmlstring):
        self._styleDoc = libxml2.parseDoc(styleXmlstring)
        self._style = libxslt.parseStylesheetDoc(self._styleDoc)
        
if __name__ == "__main__":
    pass