#!/usr/bin/env python
#
# SYNOPSIS: exec.py <node_list> <command_line>
#
# DESCRIPTION: 
#     Just a simple tool to exec command in parallel on multiple nodes.
#
#     node_list: double comma separeted list of nodes with naive
#              bash-like brace expansion.
#         e.g.  node1,,node2,,node3   -> node1, node2, node3 
#               node{1..5}            -> node1, node2, node3, node4, node5
#               node{a,b,c}           -> nodea, nodeb, nodec
#               node{1,2},,node{3..5} -> node1, node2, node3, node4, node5
#
#        NOTE: quote node_list section to avoid bash's brace expansion
#                
# written by tomoe sugihara <sugihara@valinux.co.jp>

import os
import sys
import threading
import commands
import re
import time
from nodes import *

results = []

def print_usage():
    print "Usage: pexec  node_list command_line"
    print
    print "    node_list   : list of nodes on which the command runs."
    print "                  comma separated list of node name."
    print "                  no white space in between."
    print
    print "    command_line: command line string you wish to run on the nodes."


def print_result():
    try:
        rows, columns = map(int, os.popen("stty size 2>/dev/null").read().split())
    except:
        row, columns = 24, 80

    # Header information
    bar_len = columns
    print "=" * bar_len
    print "Command: " + cmdline
    print "Nodes:   " + ", ".join(node_list)
    print "=" * bar_len

    # command outputs
    for node in sorted(results, key=lambda k: k.nodename):

        bar_left_len = 2
        print "*"*bar_left_len + " " + node.nodename + \
                "-"* (bar_len - bar_left_len - len(node.nodename) - 29  - 2) \
                 +  " Elapsed time: %8.2f (sec) " % node.elapsed_time
        print node.output


    # Summary info
    print "=" * bar_len
    n_r = zip([ r.nodename for r in results],  [ r.status for r in results])
    succeeded = filter(lambda x: x.status == 0, results)
    failed = filter(lambda x: x.status != 0, results)
    
    print "Succeeded: " + ", ".join([ n.nodename for n in succeeded])
    print "Failed   : " + ", ".join([ "%s(%d)" % (n.nodename, n.status) for n in failed])
    print "=" * bar_len

def expand_node_list(item):
    result = [item]
    m = re.search("\{(.*\,.*)\}", item)
    if m:
        b, a  = re.split("\{.*\}", item)
        in_paren = m.group(1)
        ll = in_paren.split(',')
        result = [ b + x + a for x in ll ]
    m = re.search("\{(.*\.\..*)\}", item)
    if m:
        b, a  = re.split("\{.*\}", item)
        in_paren = m.group(1)
        s, e = map(int, in_paren.split('..'))
        result = [ b + str(x) + a for x in xrange(s, e + 1)]
    return result

def flatten_nested_list(l):
    if len(l) == 0:
        return l
    if len(l) == 1:
        return l[0]
    else:
        return l[0] + flatten_nested_list(l[1:])


class Result:
    def __init__(self, nodename):
        self.nodename = nodename
        self.output = "N/A"
        self.status = 1
        self.elapsed_time = 0.0
        

#    def set_output(self, string):
#        self.output = string

#    def append_output(self, string):
#        self.output += string

    def __repr__(self):
        return self.nodename

#    def get_nodename(self):
#        return self.nodename

#    def get_output(self):
#        return self.output

#    def set_elapsed_time(self, elapsed_time):
#        self.elapsed_time = elapsed_time

#    def get_elapsed_time(self):
#        return self.elapsed_time


class Exec(threading.Thread):
    def __init__(self, nlist, cmd):
        self.cmd = cmd
        self.nlist = nlist
        threading.Thread.__init__(self)


    def run(self):
        if len(self.nlist) == 1:
            node=self.nlist[0]
            r = Result(node)
            results.append(r)

            cmd = "ping -c 2 -i 0.5 -w 1 " + node
            status,output = commands.getstatusoutput(cmd)
            if status > 0:
                r.output = "SKIPPED: the node is unreachable."
                return

            cmd = "ssh -l root " + node + " " + self.cmd
            start = time.time()
            status,output = commands.getstatusoutput(cmd)
            r.output = output
            r.status = status >> 8
            if status > 0:
                r.output += "\nStatus: %d" % (status >> 8)

            r.elapsed_time = time.time() - start
            return 

        pivot = len(self.nlist)/2
        left = self.nlist[0:pivot]
        right = self.nlist[pivot:]
        l = Exec(left, self.cmd)
        r = Exec(right, self.cmd)

        l.start()
        r.start()
        l.join()
        r.join()


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    node_spec=sys.argv[1]
    node_list=[]
    try:
        exec("node_list = " + node_spec)
    except:
        node_list = flatten_nested_list(
                       map(expand_node_list, node_spec.split(',,'))
                    )

    cmdline = " ".join(sys.argv[2:])

    t = Exec(node_list, cmdline)
    t.start()
    t.join()

    print_result()
    # take or for exit status to detect any error.
    sys.exit(int(reduce(lambda x, y: x or y,  [r.status for r in results])))
