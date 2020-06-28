#!/usr/bin/env python
import os
import sys


scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
sys.path.append(scriptPath + '/../lib')


import parsers.active
import parsers.locations
import parsers.closed

a = parsers.active.Parser()
a.get()

c = parsers.closed.Parser()
c.get()

