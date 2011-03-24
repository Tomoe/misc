#!/usr/bin/env python

import struct
import sys
from optparse import OptionParser

table = {}
def initialize_table():
    for n in range(256):
        c = n
        for k in range(8):
            if (c & 0x1):
                c = 0xedb88320 ^ (c >> 1)
            else:
                c = c >> 1
        table[n] = c


def compute_crc(contents):
    # use generator not to materialize data; 
    # more space efficient, but seems a bit slower (by several %?) than list
    bin = ( struct.unpack('B', b)[0] for b in contents ) 
    crc = 0 ^ 0xffffffff
    crc = reduce( lambda x, y: table[(x ^ y) & 0xff] ^ (x>>8), bin, crc)
    return crc ^ 0xffffffff

def compute_crc_on_blockfile(f, filename, bs):
    offset = 0
    while(True):
        contents = f.read(bs)
        if not contents:
            break
        crc = compute_crc(contents)
        print "crc32 of file %s ofset %8d : %x" % (filename, offset,  crc)
        offset += bs
    

def  compute_crc_on_file(f, filename, start, end):
    if start:
        f.seek(start)
    
    if end:
        if not start:
            start = 0
        bytes = end - start        
        contents = f.read(bytes)
    else:
        contents = f.read()
    

    crc = compute_crc(contents)

    print "crc32 of file %s start %s end %s : %x" % (filename, start, end,  crc)

    
def main():

    parser = OptionParser()
    parser.add_option("-b", "--blockfile", action="store_true")
    parser.add_option("--bs", "--blocksize", type="int", default=512)
    parser.add_option("-s", "--start", type="int")
    parser.add_option("-e", "--end", type="int")

    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        print "give me a file name"
        sys.exit(1)
    filename = args[0]
    print options
    print args
    initialize_table()
    for k,v in  table.items():
        print k, v
    try:
        f = open(filename)
    except Exception, e:
        print e
        sys.exit(1)

    if options.blockfile:
        compute_crc_on_blockfile(f, filename, options.bs)
    else:
        compute_crc_on_file(f, filename, options.start, options.end)

if __name__ == '__main__':
    main()
