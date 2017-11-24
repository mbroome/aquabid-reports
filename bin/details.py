#!/usr/bin/env python
import os
import sys
import re
import json
import time

scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
sys.path.append(scriptPath + '/../lib')

import timetools

import pprint
pp = pprint.PrettyPrinter(indent=4)

rowPattern = re.compile('.*auction\.cgi.*?>(.*?)<\/a.*?<td.*?<td.*?font.*?>(.*?)<\/font.*?<td.*?<td.*?font.*?>(.*?)<\/font.*<td>.*?>(.*?)<\/font.*')

content = open('details.html', 'r').read()

details = {
           'item': '',
           'category': '',
           'reserve': '',
           'bids': []
          }

for line in content.split('\n'):
   if 'Bidders' in line:
      #print line

      table = line.split('</tr><tr')
      #pp.pprint(table)
      for row in table:
         #pp.pprint(row)
         m = rowPattern.match(row)
         if m:
            record = {
                      'bidder': m.group(1),
                      'bidtime': m.group(2),
                      'price': m.group(3),
                      'comment': m.group(4)
                     }

            unixtime, utc = timetools.parseTimestamp(record['bidtime'])
            record['bidtime'] = unixtime
            record['utc'] = time.mktime(utc.timetuple())

            record['price'] = record['price'].rstrip()
            record['price'] = record['price'].replace('$', '')

            #pp.pprint(record)
            details['bids'].append(record)

   if 'HIDDEN' in line:
      value = line[line.find('value="') + 7:]
      value = value[:value.find('"')]
      if 'ITEM' in line:
         details['item'] = value
      elif 'CATEGORY' in line:
         details['category'] = value

   if 'Reserve price not yet met' in line:
      details['reserve'] = 'notmet'

print json.dumps(details)

