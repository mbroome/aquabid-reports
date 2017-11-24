#!/usr/bin/env python
import os
import sys
import re
import json
import pprint
pp = pprint.PrettyPrinter(indent=4)

rowPattern = re.compile('.*?><td.*?>.*?font.*?>(.*?)<\/font.*?</td><td>.*?href=\"(.*?)\">(.*?)<\/a>.*</td><td>.*?font.*?>(.*?)<\/font.*?</td><td>.*?font.*?>(.*?)<\/font.*?</td><td>.*?font.*?>(.*?)<\/font.*?</td><td>.*?font.*?>(.*?)<\/font.*?</td>.*')

content = open('closed.html', 'r').read()

content = content[content.find('Bid Price'):]
content = content[:content.find('</tbody></table>')]
content = content.replace('\n', '')
content = content[:len(content) - 5]

lines = content.split('</tr><tr')

closedList = []
for line in lines:
   if 'Bid Price' not in line:

      m = rowPattern.match(line)
      if m:
         id = m.group(2)
         id = id[id.find('?view_closed_item&amp;') + 23:]
         i = re.search('\d', id)
         if i:
            id = id[i.start():]
         record = {
                   'id': id,
                   'link': m.group(2),
                   'item': m.group(3),
                   'seller': m.group(4),
                   'closes': m.group(1),
                   'winner': m.group(5),
                   'price': m.group(6),
                   'reserve': m.group(7),
                  }

         record['price'] = record['price'].rstrip()
         record['price'] = record['price'].replace('$', '')
         try:
            f = float(record['price'])
            record['price'] = f
         except Exception, e:
            pass

         #pp.pprint(record)
         closedList.append(record)

print json.dumps(closedList)
