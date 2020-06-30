#!/usr/bin/env python
      
import os
import sys
import re
import json
import time
import requests
      
import mysql.connector
      
import timetools
import dbconn
import sanatizers
     
import pprint
pp = pprint.PrettyPrinter(indent=4)
     

class Parser():
   def get(self):
      rowPattern = re.compile('.*?font.*?>(.*?)<\/.*?href=\"(.*?)\">(.*?)<\/a>.*?font.*?>(.*?)<\/.*?font.*?>(.*?)<\/.*?font.*?>(.*?)<\/.*?font.*?>(.*?)<\/.*', re.IGNORECASE)
      
      
      url = 'https://www.aquabid.com/cgi-bin/auction/closed.cgi'
      postData = {
         'action': 'results',
         'DAYS': '3',
         'category': 'all',
         'B1': 'Submit',
      }
      print "## Post: ", url
      r = requests.post(url, postData)
      
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
            unixtime, category = sanatizers.ID(id)

            record = {
                      'id': unixtime,
                      'category': category,
                      #'utc': time.mktime(utc.timetuple()),
                      'link': m.group(2).replace('&amp;', '&'),
                      'description': m.group(3),
                      'seller': sanatizers.Seller(m.group(4)),
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
      
      #print(json.dumps(closedList))
      
      query = "UPDATE auctions set winner = %s, closed = true where id = %s and category = %s"
      
      cursor = dbconn.context.cursor()
      
      for record in closedList:
         #pp.pprint(record)
      
         data = (
            record['winner'],
            record['id'],
            record['category']
         )
      
         cursor.execute(query, data)
      
      dbconn.context.commit()
      
      cursor.close()
      
