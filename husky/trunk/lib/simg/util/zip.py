#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)


import os
import zipfile
import tarfile

import simg.io.file as fs


def extract(zippath, dest=None, members=None):
    if dest is None:
        dest = os.path.dirname(zippath) 
    
    logger.info("extract: zippath=[%s], dest=[%s]", zippath, dest)
    
    if tarfile.is_tarfile(zippath):
        tarobj = tarfile.open(zippath)
        tarobj.extractall(dest)
        tarobj.close()
    elif zipfile.is_zipfile(zippath):
        zipobj = zipfile.ZipFile(zippath)
        if members is None:
            zipobj.extractall(dest)
        else:
            for member in members:
                zipobj.extract(member, dest)
        zipobj.close()
    else:
        raise Exception("unsupported archive type")


def archive(src, zippath, exclude=None, ziptype="ZIP"):
    logger.info("archive: src=[%s], zippath=[%s], exclude=[%s], type=[%s]", src, zippath, exclude, ziptype)
    
    dirpath = os.path.dirname(zippath)
    if not os.path.exists(dirpath):
        fs.mkpath(dirpath)
    
    if ziptype == "ZIP":
        zipobj = zipfile.ZipFile(zippath, "w")
        if os.path.isdir(src):
            for found in fs.find(src, exclude=exclude):
                logger.debug("found: %s", found)
                relname = os.path.relpath(found, src)
                if relname != ".":
                    relname = relname.replace("\\", "/")
                    if os.path.isdir(found):
                        relname += "/"
                    zipobj.write(found, relname)
        else:
            zipobj.write(src, os.path.basename(src))
        zipobj.close()
    elif ziptype == "GZ" or ziptype == "BZ2":
        raise
    else:
        raise Exception("unsupported archive type")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )

