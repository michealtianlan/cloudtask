#!/usr/bin/python
"""
Launch new cloud workers and write list of addresses to a file

Cloudtask can launch and destroy cloud workers automatically when needed, but
sometimes it can be desirable to launch a persistent pool of workers and manage
it by hand.

Options:

    --apikey      Hub APIKEY
                  Environment: HUB_APIKEY

    --region      Region for instance launch (default: us-east-1)
                  Regions:

                    us-east-1 (Virginia, USA)
                    us-west-1 (California, USA)
                    eu-west-1 (Ireland, Europe)
                    ap-southeast-1 (Singapore, Asia)

    --size        Instance size (default: m1.small)
                  Sizes:

                    t1.micro (1 CPU core, 613M RAM, no tmp storage)
                    m1.small (1 CPU core, 1.7G RAM, 160G tmp storage)
                    c1.medium (2 CPU cores, 1.7G RAM, 350G tmp storage)

    --type        Instance type <s3|ebs> (default: s3)
    --label       Hub description label for all launched servers

Usage examples:

    # create workers.txt file with list of new worker addresses
    cloudtask-launch-workers 10 workers.txt

    # append list of worker addresses to a file
    cloudtask-launch-workers 10 - >> workers.txt

"""

import os
from os.path import *
import sys
import getopt

from cloudtask import Hub

def usage(e=None):
    if e:
        print >> sys.stderr, "error: " + str(e)

    print >> sys.stderr, "Usage: %s [ -opts ] howmany ( path/to/list-of-ips | - )" % sys.argv[0]
    print >> sys.stderr, __doc__.strip()
    sys.exit(1)

def fatal(e):
    print >> sys.stderr, "error: " + str(e)
    sys.exit(1)

def main():
    kwargs = {
        'region': "us-east-1",
        'size': "m1.small",
        'type': "s3",
        'label': "Cloudtask worker",
    }

    apikey = os.environ.get('HUB_APIKEY', os.environ.get('CLOUDTASK_APIKEY'))
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   'h', [ 'help',
                                          'apikey=' ] + 
                                        [ key + '=' for key in kwargs ])
    except getopt.GetoptError, e:
        usage(e)

    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()

        if opt == '--apikey':
            apikey = val

        for key in kwargs:
            if opt == '--' + key:
                kwargs[key] = val
                break

    if not apikey:
        fatal("missing required APIKEY")

    if len(args) < 2:
        usage()

    howmany, output = args

    try:
        howmany = int(howmany)
        if howmany < 1:
            raise ValueError
    except ValueError:
        usage("illegal howmany value '%s'" % howmany)

    if output == '-':
        output = sys.stdout
    else:
        if exists(output):
            fatal("'%s' already exists, refusing to overwrite" % output)

        output = file(output, "w")

    for address in Hub(apikey).launch(howmany, **kwargs):
        print >> output, address

if __name__ == "__main__":
    main()