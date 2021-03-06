#!/usr/bin/env python
from __future__ import print_function

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

# <TR bgcolor=#C0C0C0><TD colspan=6><font size=2 face=Arial>&nbsp;&nbsp;<B>Air Pumps</B></TD></TR>
titlePattern = re.compile('<tr .*<b>(.*)<\/b.*tr>', re.IGNORECASE)

# <TR BGCOLOR=#FFFFFF onMouseOver="if (!window.__cfRLUnblockHandlers) return false; this.style.backgroundColor='#BACCDE'; this.style.cursor='hand';" onMouseOut="if (!window.__cfRLUnblockHandlers) return false; this.style.backgroundColor=&quot;#FFFFFF&quot;" data-cf-modified-a45195ffae2abc17658d0216-=""><TD valign=top><font face=arial SIZE=2><A HREF="https://www.aquabid.com/cgi-bin/auction/auction.cgi?airpumps&1592785802" target=_new><img src="https://www.aquabid.com/images/newwindow.gif" border=0 alt="Open In New Window"></a>&nbsp;<A HREF="https://www.aquabid.com/cgi-bin/auction/auction.cgi?airpumps&1592785802">12 AIR STONES-TOP QUALITY-BARGAIN PRICE!! </A> <IMG align="top" border="0" SRC="https://www.aquabid.com/images/pic.gif" alt="PIC "> <IMG align="top" border="0" SRC="https://www.aquabid.com/images/us.gif" alt="Will Ship to United States Only"></TD><TD ALIGN=CENTER WIDTH=12%><font face=arial SIZE=2>Buyguy52</TD><TD ALIGN=RIGHT><font face=arial SIZE=2>6/21</TD><TD ALIGN=RIGHT><font face=arial SIZE=2><IMG SRC="https://www.aquabid.com/images/buyitnow.gif" alt="Buy it now!"></TD><TD ALIGN=RIGHT><font face=arial SIZE=2>$4.00 <IMG align="top" SRC="https://www.aquabid.com/images/icons/reserve_none.gif" border="0 alt=" No Reserve "></TD></TR>

# <TR BGCOLOR=#FFFFFF onMouseOver="if (!window.__cfRLUnblockHandlers) return false; this.style.backgroundColor='#BACCDE'; this.style.cursor='hand';" onMouseOut="if (!window.__cfRLUnblockHandlers) return false; this.style.backgroundColor=&quot;#FFFFFF&quot;" data-cf-modified-a45195ffae2abc17658d0216-=""><TD valign=top><font face=arial SIZE=2><A HREF="https://www.aquabid.com/cgi-bin/auction/auction.cgi?airpumps&1592785802" target=_new><img src="https://www.aquabid.com/images/newwindow.gif" border=0 alt="Open In New Window"></a>&nbsp;
# <A HREF="https://www.aquabid.com/cgi-bin/auction/auction.cgi?airpumps&1592785802">
# 12 AIR STONES-TOP QUALITY-BARGAIN PRICE!! 
# </A> <IMG align="top" border="0" SRC="https://www.aquabid.com/images/pic.gif" alt="PIC "> 
# <IMG align="top" border="0" SRC="https://www.aquabid.com/images/us.gif" alt="Will Ship to United States Only"></TD><TD ALIGN=CENTER WIDTH=12%>
# <font face=arial SIZE=2>Buyguy52</TD><TD ALIGN=RIGHT>
# <font face=arial SIZE=2>6/21</TD><TD ALIGN=RIGHT>
# <font face=arial SIZE=2><IMG SRC="https://www.aquabid.com/images/buyitnow.gif" alt="Buy it now!"></TD><TD ALIGN=RIGHT>
# <font face=arial SIZE=2>$4.00 <IMG align="top" SRC="https://www.aquabid.com/images/icons/reserve_none.gif" border="0 
# alt=" No Reserve "></TD></TR>
#descriptionPattern = re.compile('<tr .*?><td .*?>.*<a href=\"(https:\/\/.*?)\">(.*?)<\/a>.*?(<img .*>)<img .*SRC="(.*)" alt.*<td .*?><font.*?>(.*?)<\/td><td .*?><font .*?>(.*?)<\/.*</td><td .*?><font.*?>(.*?)<img.*\/reserve_(.*)\.gif.*?</td><\/tr>')

#                                                             link             desc             img                   seller               close                    bids                  price                reserve
descriptionPattern = re.compile('<tr .*?><td .*?>.*<a href=\"(https:\/\/.*?)\">(.*?)<\/a> +<img (.*)><\/td.*?<font .*?>(.*?)<\/td.*?<font .*?>(.*?)</td.*?<font .*?>(.*?)</td.*?<font .*?>(.*?)<img.*\/reserve_(.*)\.gif.*?</td', re.IGNORECASE)


url = 'https://www.aquabid.com/cgi-bin/auction/search.cgi'

postData = {
   'searchstring': '.*',
   'searchtype': 'keyword',
   'category': 'all',
   'searchloc': 'All'
}

r = requests.post(url, postData)

#print r.text

#sys.exit(0)

#content = open('active.html', 'r').read()
content = r.text
section = ''
found = False

activeList = []
bidList = []
for line in content.split('\n'):
   # find the start of the content in the body
   if '<B>Item</B>' in line:
      found = True
   if found:
      record = {
                'id': '',
                'section': section,
                'link': '',
                'description': '',
                'pic': '',
                'seller': '',
                'closes': '',
                'bids': '',
                'price': '',
                'reserve': '',
                'shipping': '',
               }

      
      if '>Policies</a>' in line:
         found = False
      else:
         line = line.replace('&amp;', '&')
         line = line.replace('&nbsp;', ' ')
         line = line.replace('nbsp', ' ')
         m = descriptionPattern.match(line)
         if m:
            record['link'] = m.group(1)
            record['description'] = m.group(2)
            record['pic'] = m.group(3)
            record['seller'] = m.group(4)
            record['closes'] = m.group(5)
            record['bids'] = m.group(6)
            record['price'] = m.group(7)
            record['reserve'] = m.group(8)
         else:
            t = titlePattern.match(line)
            if t:
               section = t.group(1)

         #pp.pprint(record)
         
         if record['description']:
            # sanatize the data since it's all over the place
            record['description'] = record['description'].rstrip().lstrip()

            id = record['link'][record['link'].find('?') + 1:]
            id = id[id.find('&') + 1:]
            category = record['link'][record['link'].find('?') + 1:]
            category = category[:category.find('&')]

            unixtime, utc = timetools.parseTimestamp(id)
            record['utc'] = time.mktime(utc.timetuple())
            record['id'] = unixtime
            record['category'] = category
            record['lastpolled'] = time.time()
            #record['closed'] = {}
            #record['details'] = {}

            if 'buyitnow' in record['bids']:
               record['bids'] = '-1'
            elif 'No Bids' in record['bids']:
               record['bids'] = '0'

            picData = record['pic']
            if '/us.gif' in picData:
               record['shipping'] = 'us'
            elif '/intlship.gif' in picData:
               record['shipping'] = 'intl'
            elif '/pu.gif' in picData:
               record['shipping'] = 'pickup'
            if '/contus.gif' in picData:
               record['shipping'] = 'contus'

            if 'PIC' in record['pic']:
               record['pic'] = True
            else:
               record['pic'] = False

            record['price'] = record['price'].rstrip()
            record['price'] = record['price'].replace('$', '')
            try:
               # why can there sometimes be no price...
               f = float(record['price'])
               record['price'] = f
            except Exception, e:
               pass

         #pp.pprint(record)
         #print '####'

         
            #pp.pprint(record)
            if record['seller']:
               activeList.append(record)
         

#print json.dumps(activeList)



cnx = mysql.connector.connect(user='abreports', password='abpass',
                              host='localhost',
                              database='abreports')

'''
| id          | varchar(15)  | NO   | PRI | NULL    |       |
| category    | varchar(30)  | NO   | PRI | NULL    |       |
| section     | varchar(30)  | NO   | PRI | NULL    |       |
| link        | varchar(100) | NO   |     | NULL    |       |
| description | varchar(100) | NO   |     | NULL    |       |
| pic         | tinyint(1)   | NO   |     | 0       |       |
| seller      | varchar(30)  | NO   |     | NULL    |       |
| closes      | varchar(10)  | YES  |     | NULL    |       |
| bids        | int(11)      | YES  |     | NULL    |       |
| price       | float        | YES  |     | NULL    |       |
| reserve     | varchar(5)   | YES  |     | NULL    |       |
| shipping    | varchar(10)  | YES  |     | NULL    |       |
| details     | text         | YES  |     | NULL    |       |
'''
'''{
    'bids': 'buyitnow',
    'category': u'airpumps',
    'closes': u'6/28',
    'description': u'12 AIR STONES-TOP QUALITY-BARGAIN PRICE!!',
    'id': 1593391202,
    'lastpolled': 1593351428.361803,
    'link': u'https://www.aquabid.com/cgi-bin/auction/auction.cgi?airpumps&1593391202',
    'pic': True,
    'price': 4.0,
    'reserve': u'none',
    'section': u'Air Pumps',
    'seller': u'Buyguy52',
    'shipping': 'us',
    'utc': 1593409202.0}

'''

query = ("INSERT IGNORE INTO auctions "
          "(id, category, section, link, description, pic, seller, closes, bids, price, reserve, shipping)"
          "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")

print(query)
cursor = cnx.cursor()

for record in activeList:
   #pp.pprint(record)

   data = (
      record['id'], 
      record['category'],
      record['section'], 
      record['link'], 
      record['description'], 
      record['pic'], 
      record['seller'], 
      record['closes'], 
      record['bids'], 
      record['price'], 
      record['reserve'], 
      record['shipping']
   )

   #cursor.execute(query, record)
   cursor.execute(query, data)

cnx.commit()

cursor.close()

cnx.close()

