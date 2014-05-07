#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import json

try:
    from httplib import HTTPConnection
except ImportError:
    from httplib.client import HTTPConnection


class HttpConnection(HTTPConnection):
    def __init__(self, *args, **kwargs):
        HTTPConnection.__init__(self, *args, **kwargs)
        self.headers = {}

    def request(self, url, method, body=None, headers=None):
        httpurl = "http://%s:%s%s" % (self.host, self.port, url)
        headers = headers or self.headers
        logger.debug("Request: %s %s \nRequest Headers: %s\nRequest Body: %s", method, httpurl, headers, body)
        HTTPConnection.request(self, method, url, body, headers)
        resp = HttpResponse(self.getresponse())
        logger.debug("Response: %s %s %s %s \nResponse Headers: %s\nResponse Body: %s", method, httpurl, resp.status, resp.reason, resp.headers, resp.body)
        return resp


class HttpResponse(object):
    def __init__(self, resp):
        self.status = resp.status
        self.reason = resp.reason
        self.body = resp.read()
        self.version = resp.version
        self.headers = resp.getheaders()
        resp.close()

    @property
    def json(self):
        return json.loads(self.body)


class HttpHeaders(dict):
    """A dictionary that maintains ``Http-Header-Case`` for all keys.

    Supports multiple values per key via a pair of new methods,
    `add()` and `get_list()`.  The regular dictionary interface
    returns a single value per key, with multiple values joined by a
    comma.

    >>> h = HTTPHeaders({"content-type": "text/html"})
    >>> list(h.keys())
    ['Content-Type']
    >>> h["Content-Type"]
    'text/html'

    >>> h.add("Set-Cookie", "A=B")
    >>> h.add("Set-Cookie", "C=D")
    >>> h["set-cookie"]
    'A=B,C=D'
    >>> h.get_list("set-cookie")
    ['A=B', 'C=D']

    >>> for (k,v) in sorted(h.get_all()):
    ...    print('%s: %s' % (k,v))
    ...
    Content-Type: text/html
    Set-Cookie: A=B
    Set-Cookie: C=D
    """

    def __init__(self, *args, **kwargs):
        # Don't pass args or kwargs to dict.__init__, as it will bypass
        # our __setitem__
        dict.__init__(self)
        self._as_list = {}
        self._last_key = None
        if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], HttpHeaders):
            # Copy constructor
            for key, value in args[0].get_all():
                self.add(key, value)
        else:
            # Dict-style initialization
            self.update(*args, **kwargs)

    def __setitem__(self, name, value):
        norm_name = self._normalize(name)
        dict.__setitem__(self, norm_name, value)
        self._as_list[norm_name] = [value]

    def __getitem__(self, name):
        return dict.__getitem__(self, self._normalize(name))

    def __delitem__(self, name):
        norm_name = self._normalize(name)
        dict.__delitem__(self, norm_name)
        del self._as_list[norm_name]

    def __contains__(self, name):
        norm_name = self._normalize(name)
        return dict.__contains__(self, norm_name)

    def _normalize(self, name):
        """"coNtent-TYPE" => 'Content-Type'"""
        return "-".join([w.capitalize() for w in name.split("-")])

    def add(self, name, value):
        norm_name = self._normalize(name)
        self._last_key = norm_name
        if norm_name in self:
            # bypass our override of __setitem__ since it modifies _as_list
            dict.__setitem__(self, norm_name, self[norm_name] + ',' + value)
            self._as_list[norm_name].append(value)
        else:
            self[norm_name] = value

    def get(self, name, default=None):
        return dict.get(self, self._normalize(name), default)

    def update(self, *args, **kwargs):
        # dict.update bypasses our __setitem__
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    def copy(self):
        return HttpHeaders(self)

    def get_list(self, name):
        """Returns all values for the given header as a list."""
        norm_name = self._normalize(name)
        return self._as_list.get(norm_name, [])

    def get_all(self):
        """Returns an iterable of all (name, value) pairs.

        If a header has multiple values, multiple pairs will be
        returned with the same name.
        """
        for name, values in self._as_list.items():
            for value in values:
                yield (name, value)

    def parse_line(self, line):
        """Updates the dictionary with a single header line.

        >>> h = HTTPHeaders()
        >>> h.parse_line("Content-Type: text/html")
        >>> h.get('content-type')
        'text/html'
        """
        if line[0].isspace():
            # continuation of a multi-line header
            new_part = ' ' + line.lstrip()
            self._as_list[self._last_key][-1] += new_part
            dict.__setitem__(self, self._last_key,
                             self[self._last_key] + new_part)
        else:
            name, value = line.split(":", 1)
            self.add(name, value.strip())

    @classmethod
    def parse(cls, headers):
        """Returns a dictionary from HTTP header text.

        >>> h = HTTPHeaders.parse("Content-Type: text/html\\r\\nContent-Length: 42\\r\\n")
        >>> sorted(h.items())
        [('Content-Length', '42'), ('Content-Type', 'text/html')]
        """
        h = cls()
        for line in headers.splitlines():
            if line:
                h.parse_line(line)
        return h

if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG,
        format= '%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
    headers = HttpHeaders()
    headers.add("Content-type", "text/html")
    headers.add("Content-path", "D:/")
    print(headers.get("content-type"))
    print(headers["content-type"])
    print(headers._as_list)