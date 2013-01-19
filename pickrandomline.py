#!/usr/bin/python
import sys
import random

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-q", "--quote", action="store_true",
              help="wrap output in single quotes to guard against spaces")
(options, args) = parser.parse_args()

lines = []
l = sys.stdin.readline()
while l:
    l = l.strip()
    if l != ".":
        lines.append(l)
    l = sys.stdin.readline()

if options.quote:
    sys.stdout.write("'" + random.choice(lines) + "'")
else:
    sys.stdout.write(random.choice(lines))


