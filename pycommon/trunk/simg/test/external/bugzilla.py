#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG,
        format= '%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )