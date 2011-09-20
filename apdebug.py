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

from glob import glob
import os
import socket
import re
from subprocess import Popen, PIPE
import sys
from time import sleep

def open_connection():
    """Open a connection with the webserver so we can grab the PID"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 80))
    except socket.error, e:
        sys.stderr.write("[ERROR] %s\n" %e[1])
        sys.exit(1)
    sock.send("HEAD / HTTP/1.1\r\nHost: localhost\r\nConnection: Keep-Alive\r\n\r\n")
    response = sock.recv(2048)

    return sock

def _netstat():
    """Grab the open connections from proc"""
    PROCS = ( '/proc/net/tcp', '/proc/net/tcp6' )
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

    return [ line.split() for line in output ]

def _get_pid_of_inode(inode):
    """Find the pid using inode and return it"""
    for i in glob('/proc/[0-9]*/fd/[0-9]*'):
        try:
            if re.search(inode, os.readlink(i)):
                return i.split('/')[2]
        except OSError:
            pass

def get_listener_pid(localport):
    """Find the process ID for the service accepting our connection"""
    localport = hex(localport)[2:].upper()

    # Find the inode associated with our connection
    for line in _netstat():
        if line[2].split(':')[-1] == localport:
            inode = line[9]

    return _get_pid_of_inode(inode)

def strace(pid, outfile):
    """Start the strace"""
    p = Popen(["strace", "-o", outfile, "-rfs", "512", "-p", pid], stderr=open("/dev/null",'w'))
    return p.pid

def send_request(sock, url, headers=None):
    sock.send("GET %s HTTP/1.1\r\nHost: %s\r\n\r\n" % (url, 'localhost'))
    response = sock.recv(1024)
    sock.close()
    return response

# TODO: Nicer output
def find_problems(outfile, n=5):
    """Find the n slowest system calls"""
    n = n * -1
    output = open(outfile, 'r')
    calls = output.readlines()
    # Find the amount of time that the strace slept for before we made the call
    sleepytime = calls[1].split()[1]

    # Sort the list of calls on the relative time, and find the top n
    sorted_calls = sorted(calls, key=lambda x: x.split()[1])
    top_times = [ row.split()[1] for row in sorted_calls[n:] ]

    # Replace our sleep time in the top times
    if sleepytime in top_times:
        top_times[top_times.index(sleepytime)] = sorted_calls[n-1].split()[1]

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
    sock = open_connection()
    pid = get_listener_pid(sock.getsockname()[1])
    stpid = strace(pid, outfile)
    sleep(.5)
    send_request(sock, url)
    # Send sigterm to our strace process
    os.kill(stpid,15)
    find_problems(outfile)

if __name__ == '__main__':
    main()

