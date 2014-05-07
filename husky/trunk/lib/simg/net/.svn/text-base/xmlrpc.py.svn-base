#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import socket

try:
    from xmlrpclib import ServerProxy, Transport
except ImportError:
    from xmlrpc.client import ServerProxy, Transport

#How to support XMLRPC keyword call 
#Method1: 
#_OrigMethod = xmlrpclib._Method
#class XMLRPCClientMethodDispatcher(_OrigMethod):
#    def __call__(self, *args, **kwargs):
#        return _OrigMethod.__call__(self, *(args, kwargs))
#        
#xmlrpclib._Method = XMLRPCClientMethodDispatcher
#Method2: 
class XMLRPCClient(ServerProxy):
    class TimeoutTransport(Transport):
        def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, *args, **kwargs):
            Transport.__init__(self, *args, **kwargs)
            self._timeout = timeout
    
        def make_connection(self, host):    
            conn = Transport.make_connection(self, host)
            conn.timeout = self._timeout
            return conn

    class _MethodDispatcher():
        def __init__(self, send, name):
            self.__send = send
            self.__name = name
        def __getattr__(self, name):
            return XMLRPCClient._MethodDispatcher(self.__send, "%s.%s" % (self.__name, name))
        def __call__(self, *args, **kwargs):
            return self.__send(self.__name, (args, kwargs) )
   
    def __getattr__(self, name):
        return XMLRPCClient._MethodDispatcher(self._ServerProxy__request, name)
    
    def execute(self, name, args=(), kwargs={}):
        self.__getattr__(name)(*args, **kwargs)


try:
    from SocketServer import ThreadingMixIn
except ImportError:
    from socketserver import ThreadingMixIn

try:
    from SimpleXMLRPCServer import SimpleXMLRPCDispatcher, SimpleXMLRPCServer, resolve_dotted_attribute
except ImportError:
    from xmlrpc.server import SimpleXMLRPCDispatcher, SimpleXMLRPCServer, resolve_dotted_attribute


class XMLRPCDispatcher(SimpleXMLRPCDispatcher):
    def _marshaled_dispatch(self, data, dispatch_method = None, path = None):
        self._path = path
        return SimpleXMLRPCDispatcher._marshaled_dispatch(self, data, dispatch_method, path)
        
    def _dispatch(self, method, params):
        logger.info("recv call: path=%s, method=%s, params=%s", self._path, method, params)
        func = None
        try:
            func = self.funcs[method]
        except KeyError:
            if self.instance is not None:
                if hasattr(self.instance, '_dispatch'):
                    return self.instance._dispatch(method, params)
                else:
                    try:
                        func = resolve_dotted_attribute(self.instance, method, self.allow_dotted_names)
                    except AttributeError:
                        pass

        if func is not None:
            try:
                return func(*params[0], **params[1])
            except:
                logger.exception("Exception:")
                raise
        else:
            raise Exception('method "%s" is not supported' % method)


class XMLRPCServer(ThreadingMixIn, XMLRPCDispatcher, SimpleXMLRPCServer):
    def __init__(self, *args, **kwargs):
        SimpleXMLRPCServer.__init__(self, *args, **kwargs)


import sys
try:
    from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
except ImportError:
    from xmlrpc.server import SimpleXMLRPCRequestHandler

try:
    from xmlrpclib import dumps,Fault
except ImportError:
    from xmlrpc.client import dumps,Fault


class MultiPathXMLRPCServer(XMLRPCServer):
    def __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler,
                 logRequests=True, allow_none=False, encoding=None, bind_and_activate=True):
        self.requestHandler = SimpleXMLRPCRequestHandler
        self.requestHandler.rpc_paths = ['/', '/RPC2']
        SimpleXMLRPCServer.__init__(self, addr, requestHandler, logRequests, allow_none,
                                    encoding, bind_and_activate)
        self.dispatchers = {}
        self.allow_none = allow_none
        self.encoding = encoding

    def add_dispatcher(self, path, dispatcher):
        self.requestHandler.rpc_paths.append(path)
        self.dispatchers[path] = dispatcher
        return dispatcher

    def get_dispatcher(self, path):
        return self.dispatchers[path]

    def del_dispatcher(self, path):
        if path in self.requestHandler.rpc_paths:
            self.requestHandler.rpc_paths.remove(path)
            
        if path in self.dispatchers:
            del self.dispatchers[path]
        
    def _marshaled_dispatch(self, data, dispatch_method = None, path = None):
        try:
            response = self.dispatchers[path]._marshaled_dispatch(
               data, dispatch_method, path)
        except:
            # report low level exception back to server
            # (each dispatcher should have handled their own
            # exceptions)
            exc_type, exc_value = sys.exc_info()[:2]
            response = dumps(
                Fault(1, "%s:%s" % (exc_type, exc_value)),
                encoding=self.encoding, allow_none=self.allow_none)
        return response


if __name__=="__main__":
    logging.basicConfig(
        level = logging.DEBUG, 
        format= '%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
    def test(p1, p2):
        print(p1, p2)
    srv = XMLRPCServer( ("0.0.0.0", 5973), allow_none=True)
    srv.register_function(test)
    srv.serve_forever()