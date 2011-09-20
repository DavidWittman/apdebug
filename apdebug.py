#!/usr/bin/env python
# -*- coding: utf8 -*-
""" 
 apdebug.py
 Webserver debugging script

 Copyright (c) 2011 David Wittman <david@wittman.com>

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
from subprocess import Popen, PIPE
import urlgrabber

def open_connection():
    """Open a connection with the webserver so we can grab the PID"""
    data = urlgrabber.urlread('http://localhost/')

def get_listener_pid():
    """Find the process ID for the service accepting our connection"""
    # TODO: Iterate over full output after finding our port #

    pid = str(os.getpid()) + "/"
    pyport = ''
    httpid = None
    
    output = Popen(["netstat", "-ntp"], stdout=PIPE)
    for line in output.stdout:
        columns = line.split()
    
        try:
            if columns[6].startswith(pid):
                # The is the row for our process, get our port
                pyport = columns[3].split(':')[-1]
        except IndexError:
            pass

        if columns[4].endswith(':' + pyport):
            # This is the row containing the httpd process
            httpid = columns[6].split('/')[0]

    return httpid

def strace(pid, outfile):
    """Start the strace"""
    p = Popen(["strace", "-o", outfile, "-rfs", "512", "-p", pid], stderr=open("/dev/null",'w'))
    return p.pid

def send_request(url, headers=None):
    data = urlgrabber.urlread('http://localhost' + url)

# TODO: Retrieve times for call and print in pretty format
def find_problems(outfile, n=5):
    """Find the n slowest system calls"""
    n = n * -1
    output = open(outfile, 'r')
    calls = output.readlines()

    # Sort the list of calls on the relative time, and find the top n
    sorted_calls = sorted(calls, key=lambda x: x.split()[1])
    top_times = [ row.split()[1] for row in sorted_calls[n:] ]

    """ Find the system calls which correspond with the longest delays.
        The relative times in strace correspond with the previous system call
        WARNING: not very Pythonic """
    top_calls = [ (j.split()[1], calls[i-1].split()[2:]) for i, j in enumerate(calls) if j.split()[1] in top_times ]

    # Reverse sort our new list by the times
    top_calls.sort(key=lambda x: x[0]) 
    top_calls.reverse()

    # Print
    for time, call in top_calls:
        print colors.RED + time + colors.RESET + ' ' + ' '.join(call)

class colors(object):
    RED="\033[1;31m"
    RESET="\033[0m"

def usage():
    print "usage: " + sys.argv[0] + " /url/to/strace.php"

def main():
    outfile = '/tmp/strace.out'

    if len(sys.argv) is not 2:
        usage()
        sys.exit(1)

    url = sys.argv[1]
    open_connection()
    pid = get_listener_pid()
    stpid = strace(pid, outfile)
    send_request(url)
    # Send sigterm to our strace process
    os.kill(stpid,15)
    find_problems(outfile)

if __name__ == '__main__':
    main()

