#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

import sys

if sys.platform == "win32":
    from VideoCapture import Device
elif sys.platform.startswith("linux"):
    pass
else:
    raise NotImplementedError


class WebCam(object):
    def capImage(self, name, resolution=(1280, 720)):
        logger.info("capture picture to %s", name)
        cam = Device()
        logger.debug("start camera")
        cam.setResolution(*resolution)
        cam.saveSnapshot(name)
        logger.debug("capture picture")

    def capVideo(self, name):
        NotImplementedError

if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG, 
        format= '%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )