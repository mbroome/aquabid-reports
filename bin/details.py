#!/usr/bin/env python
import os
import sys
import re
import json
import time
import requests

import mysql.connector

scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
sys.path.append(scriptPath + '/../lib')

import timetools

import pprint
pp = pprint.PrettyPrinter(indent=4)


patternMap = {
   'closed': {
      # <td width="13%"><font size="2">Started</font></td><td width="31%"><font size="2">Nov 19 2017 - 08:10:13 AM</font></td><td width="1%"></td><td width="10%"><font size="2">Location</font></td><td width="45%"><font size="2">thailand Kanchanaburi 71260 Thailand</font></td>
      'loc': re.compile('.*>Location.*font .*?>(.*?)</font', re.IGNORECASE),

      # <td width="13%"><font size="2">Seller</font></td></font><td width="31%" colspan="4"><font size="2"><a href="https://www.aquabid.com/cgi-bin/auction/auction.cgi?askaq&Ake_betta">Ake_betta</a> (<a href="https://www.aquabid.com/cgi-bin/auction/vfb.cgi?&&vfb&Ake_betta">476/493</a>) <img src="https://www.aquabid.com/images/yellow.gif" alt="101-500" border="0"></a></font></td>
      'seller': re.compile('.*?>Seller.*auction.cgi.*?>(.*?)<.*', re.IGNORECASE),
   },
   'active': {
      # <td height="19" width="75"><font FACE="Arial" size="2">Location</font></td><td height="19" width="294"><font FACE="Arial" size="2"><a href="https://www.google.com/maps?q=Youngstown+OH+44515+United+States&hl=en" target=_new><IMG align="top" SRC="https://www.aquabid.com/images/icons/mapit.gif" border="0 alt=" Map "> Youngstown OH 44515 United States</a></font></td><td height="19" width="17">&nbsp;</td><td height="19" width="374" colspan="2"><font FACE="Arial" size="2"><a href="https://www.aquabid.com/cgi-bin/auction/vfb.cgi?1&1&vfb&Bds826"><img src="https://www.aquabid.com/images/icon_feedback.gif" border="0"> (View Seller's Feedback)</a> </font></td>
      'loc': re.compile('.*>Location.*font .*<img.*>(.*?)</a.*<a', re.IGNORECASE),

      # <td height="16" width="75"></td><td height="16" width="294"></td><td height="16" width="17"></td><td height="16"></td><td height="16" width="187"></td></tr></font><tr><td height="19" width="75"><font FACE="Arial" size="2">Seller</font></td><td height="19" width="294"><font FACE="Arial" size="2"><a href="https://www.aquabid.com/cgi-bin/auction/vfb.cgi?&&vfb&Bds826">Bds826</a> (<a href="https://www.aquabid.com/cgi-bin/auction/vfb.cgi?&&vfb&Bds826">158/158</a>) <img src="https://www.aquabid.com/images/yellow.gif" alt="101-500" border="0"></a></font></td><td height="19" width="17">&nbsp;</td><td height="19" width="374" colspan="2"><font FACE="Arial" size="2"><img src="https://www.aquabid.com/images/icon_mag.gif" border="0"> (View <a href=/cgi-bin/auction/auction.cgi?disp&viewseller&Bds826>All Seller's Auctions</a> or <a href=/cgi-bin/auction/auction.cgi?disp&viewseller&Bds826&&fwbettas>This Category</a>)</a></font></td>
      'seller': re.compile('.*?>Seller.*?vfb.cgi.*?>(.*?)</a.*', re.IGNORECASE),
   }
}

descPattern = re.compile('.*blockquote>(.*?)</blockquote', re.IGNORECASE)

# closed example
category = 'books'
id = 1592530201

# open example
#category = 'fwbettas'
#id = 1592971203

id = 1593355809
category = 'fwbettashm'

id = 1594649345
category = 'fwkillifish'

activeUrl = 'https://www.aquabid.com/cgi-bin/auction/auction.cgi?%s&%s' % (category, id)
closedUrl = 'https://www.aquabid.com/cgi-bin/auction/closed.cgi?view_closed_item&%s%s' % (category, id)

#url = 'https://www.aquabid.com/cgi-bin/auction/auction.cgi?books&1592530201'


r = requests.get(activeUrl)
if r.text.lower().find('this item has closed') > 0:
   r = requests.get(closedUrl)
#   print '### closed'
#else:
#   print '### not closed'

content = r.text.encode('utf-8').strip()
#print(content)

#sys.exit(0)


#content = open('details.html', 'r').read()

details = content
details = details.replace('\n', '')

recordType = 'closed'
if 'Current Auction Time' in content:
   content = content[content.find('Current Auction Time'):]
else:
   recordType = 'active'
   content = content[content.find('tracking.cgi'):]
   #content = content[content.lower().find('<table')+6:]

#print content
content = content[content.lower().find('<tr>'):]
content = content.replace('\n', '')

#print content

lines = re.split('<\/tr><tr>', content, flags=re.IGNORECASE)

#print lines
record = {
   'seller': '',
   'location': '',
   'details': '',
   'recordType': recordType,
}

#print recordType

for line in lines:
   #print '###'
   #print line
   m = patternMap[recordType]['loc'].match(line)
   if m:
      #print m.group(1)
      record['location'] = m.group(1).lower().lstrip().rstrip().encode('utf-8').strip()
   else:
      m = patternMap[recordType]['seller'].match(line)
      if m:
         #print m.group(1)
         record['seller'] = m.group(1).lower().lstrip().rstrip().encode('utf-8').strip()

   #print ''


m = descPattern.match(details)
if m:
    record['details'] = m.group(1).encode('utf-8').strip()

print(json.dumps(record))


cnx = mysql.connector.connect(user='abreports', password='abpass',
                              host='localhost',
                              database='abreports')

cursor = cnx.cursor()

data = open('etc/locations.json', 'r').read()
locations = json.loads(data)

query = 'INSERT IGNORE INTO sellers (user, location, country) VALUES (%s,%s,%s)'

for loc in locations:
   if record['location'].endswith(loc.lower().encode('utf-8').strip()):
      data = (
         record['seller'],
         record['location'],
         loc
      )

      cursor.execute(query, data)

cnx.commit()

cursor.close()

cnx.close()


