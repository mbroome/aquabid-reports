#!/usr/bin/env python
import os
import sys
import re
import json
import time
import pprint
pp = pprint.PrettyPrinter(indent=4)

rowPattern = re.compile('<tr .*?<td .*?Open In.*?href=\"(.*?)\">.*?a href.*?>(.*?)<\/a>(.*?)<\/td><td.*?a href.*?>(.*?)<\/a>.*?font.*?>(.*?)<\/td.*<td.*?>(.*?)<\/td.*\/tr>')

content = open('ending.html', 'r').read()
content = content.replace('<font size="2" face="Arial">', '')
content = content.replace('</font>', '')

found = False

now = time.time()

endingList = []
for line in content.split('\n'):
   if 'Item #' in line:
      found = True

   if found:
      line = line.replace('&amp;', '&')
      line = line.replace('&nbsp;', ' ')
      line = line.replace('nbsp', ' ')

      if '/cgi-bin/auction/auction.cgi' in line and line.startswith('<tr'):
         record = {
                   'id': '',
                   'link': '',
                   'item': '',
                   'seller': '',
                   'timer': '',
                   'price': '',
                  }

 
         #print line
         m = rowPattern.match(line)
         if m:
            record['link'] = m.group(1)
            record['item'] = m.group(2)
            record['seller'] = m.group(4)
            record['timer'] = m.group(5)
            record['price'] = m.group(6)

            # sanatize the data since it's all over the place
            id = record['link'][record['link'].find('?') + 1:]
            id = id[id.find('&') + 1:]
            record['id'] = id

            record['timer'] = record['timer'].lstrip(' ')

            pp.pprint(record)

#print json.dumps(endingList)
