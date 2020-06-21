#!/usr/bin/env python
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

#    ' BGCOLOR=#FFFFFF onMouseOver="this.style.backgroundColor=\'#BACCDE\'; this.style.cursor=\'hand\';" onMouseOut=this.style.backgroundColor="#FFFFFF"><TD><center><B><font size=2>6/18</center><TD><center><B><font size=2><A HREF="https://www.aquabid.com/cgi-bin/auction/closed.cgi?view_closed_item&books1592530201">Shipping Tips for Fish Hobbyists w/Shipping!</A></center></TD><TD><center><B><font size=2>Finny</center></TD><TD><center><B><font size=2>None</center></TD><TD><center><B><font size=2>---</center></TD><TD><center><B><font size=2>No Bids</center></TD>',

#                                              close                             link                                    seller                             bidder                             bid                                reserve
rowPattern = re.compile('.*?font.*?>(.*?)<\/.*?href=\"(.*?)\">(.*?)<\/a>.*?font.*?>(.*?)<\/.*?font.*?>(.*?)<\/.*?font.*?>(.*?)<\/.*?font.*?>(.*?)<\/.*', re.IGNORECASE)


url = 'https://www.aquabid.com/cgi-bin/auction/closed.cgi'
postData = {
   'action': 'results',
   'DAYS': '3',
   'category': 'all',
   'B1': 'Submit',
}
r = requests.post(url, postData)

#print r.text

#sys.exit(0)

#content = open('closed.html', 'r').read()
content = r.text

content = content[content.find('Reserve Met'):]
content = content[content.find('</TR>') + 5:]
content = content[:content.find('</TABLE')]
content = content.replace('\n', '')
#content = content[:len(content) - 5]

lines = content.split('</TR><TR')
#pp.pprint(lines)

closedList = []
for line in lines:
   m = rowPattern.match(line)
   if m:
      id = m.group(2)
      id = id[id.find('?view_closed_item&') + 18:]
      #print id
      i = re.search('\d', id)
      if i:
         category = id[:i.start()]
         id = id[i.start():]
         unixtime, utc = timetools.parseTimestamp(id)

      record = {
                'id': unixtime,
                'category': category,
                'utc': time.mktime(utc.timetuple()),
                'link': m.group(2).replace('&amp;', '&'),
                'description': m.group(3),
                'seller': m.group(4),
                'closes': m.group(1),
                'winner': m.group(5),
                'price': m.group(6),
                'reserve': m.group(7),
               }

      record['lastpolled'] = time.time()
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

