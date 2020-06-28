#!/usr/bin/env python
from __future__ import print_function

import os
import sys
import re
import json
import time
import requests

scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
sys.path.append(scriptPath + '/../lib')

import timetools

import pprint
pp = pprint.PrettyPrinter(indent=4)


url = 'https://www.aquabid.com/cgi-bin/auction/search.cgi'

r = requests.get(url)

#print r.text

#sys.exit(0)

countryList = []

content = r.text
content = content[content.lower().find('option name=sellerloc'):]
content = content[:content.lower().find('</select')]

for line in content.split('\n'):
   #print(line)
   country = line[line.find('>')+1:]
   country = country[:country.find('<')]
   if country and country[0] == '-':
      country = country[country.find(' '):]
   country = country.lstrip().rstrip()

   if country and country != 'All Countries':
      countryList.append(country)

print(json.dumps(countryList))


