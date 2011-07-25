#!/usr/bin/python
"""
Destroy + unregister cloud workers and remove their addresses from file listing

Options:

    --apikey      Hub APIKEY
                  Environment: HUB_APIKEY

Return codes:

    0   destroyed all workers
    1   fatal error
    2   couldn't destroy some workers

Usage example:

    cloudtask-destroy-workers worker-ips.txt
    cat workers-ips | cloudtask-destroy-workers -

"""

import os
import sys
import getopt

from cloudtask import Hub

def usage(e=None):
    if e:
        print >> sys.stderr, "error: " + str(e)

    print >> sys.stderr, "Usage: %s [ -opts ] ( path/to/list-of-ips | - )" % sys.argv[0]
    print >> sys.stderr, __doc__.strip()
    sys.exit(1)

def fatal(e):
    print >> sys.stderr, "error: " + str(e)
    sys.exit(1)

def main():
    apikey = os.environ.get('HUB_APIKEY', os.environ.get('CLOUDTASK_APIKEY'))
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   'h', [ 'help',
                                          'apikey=' ])
    except getopt.GetoptError, e:
        usage(e)

    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()

        if opt == '--apikey':
            apikey = val

    if not apikey:
        fatal("missing required APIKEY")

    if not len(args) == 1:
        usage()

    input = args[0]
    if input == '-':
        fh = sys.stdin
    else:
        fh = file(input)

    addresses = fh.read().splitlines()
    if not addresses:
        print "no workers to destroy"
        return
    
    destroyed = Hub(apikey).destroy(addresses)
    if not destroyed:
        fatal("couldn't destroy any workers")
    
    addresses_left = list(set(addresses) - set(destroyed))
    if addresses_left:
        print >> sys.stderr, "warning: can't destroy " + " ".join(addresses_left)

        addresses_left.sort()
        if input != '-':
            fh = file(input, "w")
            for address in addresses_left:
                print >> fh, address
            fh.close()

        sys.exit(2)

    if not addresses_left:
        if input != '-':
            os.remove(input)

        sys.exit(0)

if __name__ == "__main__":
    main()
