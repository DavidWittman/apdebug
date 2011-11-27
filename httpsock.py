#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import socket
import re
import sys
from glob import glob

class HttpSock(socket.socket):
    """A simple HTTP client for debugging purposes.
    
    Args:
        hostname: The HTTP server to establish a connection with

    """

    def __init__(self, hostname):
        self.hostname = hostname
        super(HttpSock, self).__init__(socket.AF_INET, socket.SOCK_STREAM)

    def open(self):
        """Initiates a connection to the local HTTP Server

        Returns:
            A string containing the response from a HEAD request.

        """

        try:
            self.connect((self.hostname, 80))
        except socket.error, e:
            sys.stderr.write("[ERROR] %s\n" % e[1])
            sys.exit(1)
        self.send("HEAD / HTTP/1.1\r\nHost: %s\r\nConnection: Keep-Alive\r\n\r\n"
            % self.hostname)
        response = self.recv(1024)
        self.pid = self._get_listener_pid()

        return response

    def get(self, hostname, url, headers=None):
        """Issues a GET request

        Args:
            hostname: A string containing the contents of the Host 
                header to be passed with the HTTP request.
            url: A string representing the URL to be tested. Accepts
                http://example.com/index.php,
                example.com/index.php,
                localhost/index.php
            headers: A dictionary of HTTP headers to include in the
                request

        Returns:
            A string containing a response from the request.

        >>> h = HttpSock('http://example.com')
        >>> h.open()
        >>> h.get('example.com', '/foo/bar.php')
        It works!

        """

        # Form the request
        request = ["GET %s HTTP/1.1" % url, "Host: %s" % hostname]
        if headers:
            request.extend([k + ': ' + v for k, v in headers.items()])
        # Extend with two empty values for trailing \r\n\r\n
        request.extend(['',''])
        
        # Send, receive, and close
        self.send('\r\n'.join(request))
        response = self.recv(1024)
        self.close()

        return response

    def _netstat(self):
        """Grab the open connections from proc"""
        PROCS = ('/proc/net/tcp', '/proc/net/tcp6')
        output = []

        for procfile in PROCS:
            try:
                fd = open(procfile, 'r')
            except:
                return None
            else:
                content = fd.readlines()
                content.pop(0)
                fd.close()
                output.extend(content)

        return [line.split() for line in output]

    def _get_listener_pid(self):
        """Finds the process ID for the service accepting our
        socket connection locally.
        
        """
        localport = self.getsockname()[1]
        localport = hex(localport)[2:].upper()

        # Find the inode associated with our connection
        for line in self._netstat():
            if line[2].split(':')[-1] == localport:
                inode = line[9]

        return self._get_pid_of_inode(inode)

    def _get_pid_of_inode(self, inode):
        """Find the pid using inode and return it"""
        for i in glob('/proc/[0-9]*/fd/[0-9]*'):
            try:
                if re.search(inode, os.readlink(i)):
                    return i.split('/')[2]
            except OSError:
                pass
