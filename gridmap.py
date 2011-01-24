#! /usr/bin/env python

import sys

from cStringIO import StringIO
from optparse import OptionParser
import random
import re
from repoman_client import repoman_client


usage = "Usage: use this file in conjunction with a gridmap file by using the "\
    "-f or --file option, followed by the path to the file. %prog [options] arg"
parser = OptionParser(usage)
parser.add_option("-f", "--file", dest="filename",
                  help="The location of the gridmap file to add.",
                  metavar="FILE", default=None)
parser.add_option("-o", "--output", dest="outfile",
                  help="The location of the error file to write", metavar="FILE",
                  default=None)
(options, args) = parser.parse_args()
if options.filename is None:
    print "It's is nessecary to specify -f FILE for this program to run"
    sys.exit(1)
try:
    f = open(options.filename, 'r')
except:
    print "Unable to open file, please try entering command again."
    sys.exit(1)
if options.outfile != None:
    standard_stdout = sys.stdout
    w = open(options.outfile, "w")
    sys.stdout = w
repo = repoman_client.repoman_client()
linenum = 0
passnum = 0
failnum = 0
for L in f:
    linenum += 1
    dnmess = ""
    cnmess = ""
    unmess = ""
    dn = re.search("^\".*[A-Z,a-z,1-9].*\"", L)
    if dn is not None:
        dn = dn.group(0)
        cn = re.search("CN=[A-Z,a-z,1-9].+\"", L)
        if cn is not None:
            fn = cn.group(0)
            fn = fn[3:]
            fn = "\"" + fn
            un = re.search("[A-Z,a-z,1-9]+$", L)
            if un is not None:
                un = un.group(0)
                email = un
                email = email + "_" + str(random.randint(0, 999)) + \
                    "@fakemail.com"
                metadata = dict([("user_name", un), ("email", email), \
                                ("cert_dn", dn), ("full_name", fn)])
                try:
                    if options.outfile != None:
                        old_out = w
                    else:
                        old_out = sys.stdout
                    sys.stdout = stdout = StringIO()
                    repo.create_user(metadata)
                    sys.stdout = old_out
                    from_repo = stdout.getvalue()
                    if re.search("Username or client_dn conflict", from_repo) \
                    is not None:
                        result = "Failure. Username or DN conflict," + \
                        " name may already be created"
                        failnum += 1
                    else:
                        result = "Success. " + un + " created as a user."
                        passnum += 1
                except:
                    result = "Failure. Unable to create account for unknown" + \
                    "reasons. Check input and temporary proxies. \n"
                    failnum += 1
            else:
                result = "Failure. Cannot find username"
                failnum += 1
        else:
            result = "Failure. Cannot find common name"
            failnum += 1
    else:
        if not L.strip():
            continue
        else:
            result = "Failure. Cannot find distinguished name"
            failnum += 1
    output = "Line number " + str(linenum) + ": " + result
    print output
if options.outfile != None:
    print "Final result: \n" + str(passnum) + " successes, " + str(failnum) + \
    " failures."
    sys.stdout = standard_stdout
print "Final result: \n" + str(passnum) + " successes, " + str(failnum) + \
    " failures."