#!/usr/bin/env python

import sys

for line in sys.stdin:
    line = line.strip()
    if line.startswith('reduce'):
        print '\t'.join(line.split()[1:])
