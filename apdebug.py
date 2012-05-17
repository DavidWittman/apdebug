#!/usr/bin/env python
# -*- coding: utf8 -*-
""" 
 apdebug.py
 Webserver debugging script

 Copyright (c) 2012 David Wittman <david@wittman.com>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

import os
import sys
from time import sleep
from subprocess import Popen, PIPE

import utils

class ApDebug(object):
    """ Starts the webserver debugger
    
    :param url: The URL to strace
    :type url: string

    >>> ap = ApDebug('http://example.com/foo.php')
    >>> ap.strace('/tmp/strace.out')
    """

    def __init__(self, url):
        self.url = utils.Url(url)
        self.http = utils.HttpSock('localhost')

    class colors(object):
        RED="\033[1;31m"
        RESET="\033[0m"

    def _strace(self, pid):
        """System call to strace"""
        p = Popen(["strace", "-o", self.outfile, "-rfs", "512", "-p", pid], 
                    stderr=open("/dev/null",'w'))
        return p.pid

    def strace(self, outfile):
        """Start the strace"""
        self.outfile = outfile
        self.http.open()
        stpid = self._strace(self.http.pid)
        sleep(.5)
        self.http.get(self.url.hostname, self.url.request)
        # Send SIGTERM to our strace process
        os.kill(stpid, 15)
        self.find_slow_calls()

    def get_queries(self):
        """Find and return a list of MySQL queries executed within the strace"""
        pass

    # TODO: convert to get_slow_calls and return a list
    def find_slow_calls(self, n=5):
        """Find the n slowest system calls"""
        def call_time(call):
            return call.split()[1]

        n = n * -1
        output = open(self.outfile, 'r')
        calls = output.readlines()
        # Find the amount of time that the strace slept for before we made the call
        sleepytime = call_time(calls[1])

        # Make sure we grab the right one. This could use some improvement
        if float(sleepytime) < .1:
            sleepytime = call_time(calls[2])

        # Sort the list of calls on the relative time, and find the top n
        sorted_calls = sorted(calls, key=call_time)
        top_times = [call_time(row) for row in sorted_calls[n:]]

        # Replace our sleep time in the top times
        if sleepytime in top_times:
            top_times[top_times.index(sleepytime)] = call_time(
                sorted_calls[n-1])

        """ Find the system calls which correspond with the longest 
            delays.  The relative times in strace correspond with 
            the previous system call.  WARNING: not very Pythonic     
        """
        slow_calls = [(i-1, call_time(j), calls[i-1].split()[2:]) 
            for i, j in enumerate(calls) if call_time(j) in top_times]

        # Reverse sort our new list by the times
        slow_calls.sort(key=lambda x: x[1])
        slow_calls.reverse()

        # Print
        for linenum, time, call in slow_calls:
            print "%s%s%s %s" % (self.colors.RED, 
                                time, 
                                self.colors.RESET, 
                                ' '.join(call))

    @classmethod
    def usage(self):
        print "usage: " + sys.argv[0] + " /url/to/strace.php"

if __name__ == '__main__':
    if len(sys.argv) is not 2:
        ApDebug.usage()
        sys.exit(1)
    ad = ApDebug(sys.argv[1])
    ad.strace('/tmp/strace.out')

