#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import stat
import errno
import sys
import shutil
import re

if sys.platform.startswith("linux"):
    import pwd #@UnresolvedImport


def find(path, bydepth=True, exclude=None, topdir=True, topdown=True):
    """
    @:param bydepth: Reports the name of a directory only AFTER all its entries have been reported
    @:param exclude: a string or re pattern type, use this to exclude the path you don't want to find
    @:param topdir: whether include the topdir path
    @:param topdown: find the path with top->down or down->top
    """
    if not os.path.exists(path):
        raise OSError(errno.ENOENT, "No such file or directory: '%s'" % path)

    if exclude is not None and not isinstance(exclude, re._pattern_type):
        exclude = re.compile(exclude)

    def walkdir(dirpath, bydepth, exclude):
        names = os.listdir(dirpath)
        if not topdown:
            names.reverse()
            
        for name in names:
            found = os.path.join(dirpath, name)
            
            if exclude and exclude.search(found):
                logger.info("walk: skip %s", found)
                continue

            logger.log(logging.NOTSET, "walk: process %s", found)
            if not bydepth:
                yield found
            if os.path.isdir(found):
                for x in walkdir(found, bydepth, exclude):
                    yield x
            if bydepth:
                yield found
    
    if os.path.isdir(path):
        if topdir and not bydepth:
            yield path
        for x in walkdir(path, bydepth, exclude):
            yield x
        if topdir and bydepth:
            yield path
    else:
        yield path


def chmod(path, mode, recursive=False, exclude=None):
    logger.info("chmod: path=%s, mode=%s, recursive=%s, exclude=%s", path, mode, recursive, exclude)
    
    for found in find(path, False, exclude):
        os.chmod(found, mode)


def chown(path, user=None, group=None, recursive=False, exclude=None):
    logger.info("chown: path=%s, user=%s, group=%s, recursive=%s, exclude=%s", path, user, group, recursive, exclude)
    
    uid = pwd.getpwnam(user).pw_uid  if user else -1
    gid = pwd.getpwnam(group).pw_gid if group else -1
    for found in find(path, False, exclude):
        os.chown(found, uid, gid)   #@UndefinedVariable


def mkpath(path, mode=0o777):    
    if os.path.exists(path):
        if os.path.isdir(path):
            logger.log(logging.NOTSET, "mkpath: exists '%s', type is dir, skip", path)
        else:
            raise Exception("mkpath failed, path '%s' already exists, type is file" % path)
    else:
        logger.log(logging.NOTSET, "mkpath: non-exists '%s' ", path)
        head, tail = os.path.split(path)
        if not tail:   # no tail when xxx/newdir
            head, tail = os.path.split(head)
        if head and tail:
            mkpath(head, mode)
            if tail != os.path.curdir:   # xxx/newdir/. exists if xxx/newdir exists
                logger.info("mkpath: path=[%s], mode=[%s]", path, mode)
                os.mkdir(path, mode)


def copy(src, dst, exclude=None):
    logger.info("copy: src=%s, dst=%s, exclude=%s", src, dst, exclude)
    
    num_of_dirs  = 0
    num_of_files = 0
    
    def _copyfile(src, dst):
        try:
            shutil.copy2(src, dst)
        except IOError as ioerr:
            if ioerr.errno == errno.ENOENT:
                raise
            elif ioerr.errno == errno.EACCES:
                logger.warn("copy: dst %s is 'permission denied', remove it and retry", dst)
                os.remove(dst)
                shutil.copy2(src, dst)
                logger.log(logging.NOTSET, "copy: copy %s -> %s successfully ", src, dst)
            else:
                pass
    
    if os.path.isdir(src):
        if not os.path.exists(dst):
            mkpath(dst)
        for found in find(src, False, exclude, topdir=False):
            relpath = os.path.relpath(found, src)
            abspath = os.path.join(dst, relpath)
            if os.path.isdir(found):
                if not os.path.exists(abspath):
                    os.mkdir(abspath)
                num_of_dirs += 1
            else:
                logger.log(logging.NOTSET, "copy: %s -> %s", found, abspath )
                _copyfile(found, abspath)
                num_of_files += 1
#    elif os.path.islink(src):
#        linkto = os.readlink(src)   #@UndefinedVariable
#        os.symlink(linkto, dst)     #@UndefinedVariable
    else:
        if not os.path.exists(dst):
            if dst.endswith("\\") or dst.endswith("/"):
                mkpath(dst)
            else:
                mkpath(os.path.dirname(dst))
        logger.log(logging.NOTSET, "copy: %s -> %s", src, dst )
        _copyfile(src, dst)
        num_of_files += 1
    
    logger.info("copy %s files and %s dirs to %s", num_of_files, num_of_dirs, dst)
    return num_of_dirs, num_of_files


def remove(path, exclude=None):
    logger.info("remove: path=[%s], exclude=[%s]", path, exclude )

    num_of_dirs  = 0
    num_of_files = 0
    
    for found in find(path, True, exclude, True):
        if os.path.isdir(found):
            os.rmdir(found)
            num_of_dirs += 1
        else:
            try:
                os.remove(found)
            except WindowsError as werr:
                if werr.errno == errno.EACCES:
                    logger.debug("remove: %s access is denied, chmod its mode to S_IWRITE and retry", found)           
                    os.chmod(found, stat.S_IWRITE)
                    os.remove(found)
                    logger.debug("remove: remove %s successfully", found)
                else:
                    pass
            num_of_files += 1
    logger.info("removed %s files and %s dirs from %s", num_of_files, num_of_dirs, path)
    return num_of_dirs, num_of_files


#TODO:
def move(src, dst, exclude=None):
    logger.info("move: src=[%s], dst=[%s], exclude=[%s]", src, dst, exclude)
#    def _movefile(src, dst):
#        try:
#            real_dst = dst
#            if os.path.isdir(dst):
#                real_dst = os.path.join(dst, os.path.basename(src))
#            os.rename(src, real_dst)
#        except:
#            copy(src, dst)
#            remove(src)
#    
    copy(src, dst, exclude)
    remove(src, exclude)


def touch(path, time=None):
    logger.info("touch: path=%s, time=%s", path, time )
    if not os.path.exists(path):
        dirname = os.path.dirname(path)
        if os.path.isdir(dirname):
            with open(path, 'wb') as fdst:
                fdst.write("")
            fdst.close()
        else:
            mkpath(os.path.dirname(path))
    os.utime(path, time)
    

def link(src, link):
    raise NotImplementedError


def symlink(src, link):
    raise NotImplementedError


def isSame(src, dst):
    return shutil._samefile(src, dst)

if __name__=="__main__":
    logging.basicConfig(
        level=logging.NOTSET,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
    for found in find(r"D:\Java\jaxrs-ri-2.6\jaxrs-ri", bydepth=False):
        print found

    copy(r"D:\Java\jaxrs-ri-2.6\jaxrs-ri", r"D:\test")
    remove(r"D:\test")