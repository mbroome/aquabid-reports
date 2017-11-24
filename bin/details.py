#!/usr/bin/env python
import os
import sys
import re
import json
import time
import pytz
import dateutil
import dateutil.parser

import pprint
pp = pprint.PrettyPrinter(indent=4)

TZINFOS = {
    'CDT': pytz.timezone('US/Central'),
    # ... add more to handle other timezones
    # (I wish pytz had a list of common abbreviations)
}

to_zone = dateutil.tz.tzlocal()

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
            # dates suck to parse
            record['bidtime'] = record['bidtime'].replace(' - ', ' ')
            parts = record['bidtime'].split(' ')
            # from = Fri Nov 24 2017 - 12:17:24 AM CDT	
            # to =   11:45:00 Aug 13, 2008 CDT

            ft = '%s %s %s, %s %s' % (parts[4], parts[1], parts[2], parts[3], parts[6])
            #print ft
            # parse as the CDT timezone
            t = dateutil.parser.parse(ft, tzinfos=TZINFOS)
            #pp.pprint(t)
            # utc the time
            utc = t.astimezone(pytz.utc)
            #pp.pprint(utc)
            # localtime the time
            lt = utc.astimezone(to_zone)
            #pp.pprint(lt)
            # unixtime the time
            unixtime = time.mktime(lt.timetuple())
            record['bidtime'] = unixtime
            #pp.pprint(unixtime)

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

