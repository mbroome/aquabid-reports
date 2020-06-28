#!/usr/bin/env python
import os
import sys
import re
import json
import time
import requests
      
import mysql.connector
      
import dbconn
import timetools
      
import pprint
pp = pprint.PrettyPrinter(indent=4)
      
      
class Parser():
   def get(self, id, category, seller=''):
      patternMap = {
         'closed': {
            'loc': re.compile('.*>Location.*font .*?>(.*?)</font', re.IGNORECASE),
      
            'seller': re.compile('.*?>Seller.*auction.cgi.*?>(.*?)<.*', re.IGNORECASE),
         },
         'active': {
            'loc': re.compile('.*>Location.*font .*<img.*>(.*?)</a.*<a', re.IGNORECASE),
      
            'seller': re.compile('.*?>Seller.*?vfb.cgi.*?>(.*?)</a.*', re.IGNORECASE),
         }
      }
      
      descPattern = re.compile('.*blockquote>(.*?)</blockquote', re.IGNORECASE)
      
      # closed example
      #category = 'books'
      #id = 1592530201
      
      # open example
      #category = 'fwbettas'
      #id = 1592971203
      
      #id = 1593355809
      #category = 'fwbettashm'
      
      #id = 1594649345
      #category = 'fwkillifish'
      
      activeUrl = 'https://www.aquabid.com/cgi-bin/auction/auction.cgi?%s&%s' % (category, id)
      closedUrl = 'https://www.aquabid.com/cgi-bin/auction/closed.cgi?view_closed_item&%s%s' % (category, id)
      
      print('time: ', time.time())

      if seller:
         cursor = dbconn.context.cursor()
         seller = seller.encode('utf-8').strip()

         print('id: ', id, ' category: ', category, ' seller: ', seller)
         query = "SELECT * from sellers where user = %s"

         cursor.execute(query, (seller,))
         cursor.fetchall()
         found = cursor.rowcount

         cursor.close()
         if found:
            print('## found seller, no need for details')
            return True
      
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
      
      
      #m = descPattern.match(details)
      #if m:
      #    record['details'] = m.group(1).encode('utf-8').strip()
      
      #print(json.dumps(record))
      
      
      cursor = dbconn.context.cursor()
      
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
      
      dbconn.context.commit()
      
      cursor.close()
      

      
