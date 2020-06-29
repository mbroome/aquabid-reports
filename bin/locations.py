#!/usr/bin/env python
import os
import sys


scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
sys.path.append(scriptPath + '/../lib')


import parsers.locations

p = parsers.locations.Parser()
p.get()


