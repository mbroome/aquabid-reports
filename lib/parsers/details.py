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
import sanatizers
      
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
      zipcodePattern = re.compile('\d\d\d\d\d', re.IGNORECASE)
      
      activeUrl = 'https://www.aquabid.com/cgi-bin/auction/auction.cgi?%s&%s' % (category, id)
      closedUrl = 'https://www.aquabid.com/cgi-bin/auction/closed.cgi?view_closed_item&%s%s' % (category, id)
      
      #print('time: ', time.time())

      if seller:
         cursor = dbconn.context.cursor()
         seller = sanatizers.Seller(seller)

         #print('id: ', id, ' category: ', category, ' seller: ', seller)
         query = "SELECT * from sellers where user = %s"

         cursor.execute(query, (seller,))
         cursor.fetchall()
         found = cursor.rowcount

         cursor.close()
         if found > 0:
            #print('## found seller, no need for details')
            return True
      
      print "## Get: ", activeUrl
      r = requests.get(activeUrl)
      if r.text.lower().find('this item has closed') > 0:
         print "## Get: ", closedUrl
         r = requests.get(closedUrl)
      
      content = r.text.encode('utf-8').strip()
      #print(content)
      
      #details = content
      #details = details.replace('\n', '')
      
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
      
      #print(json.dumps(lines))
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
         if m and not record['location']:
            #print '#### match: ', m.group(1)
            l = m.group(1)
            #l = re.sub(r'[^\w]', '', l)
            l = re.sub(r'[^ -~_].*', '', l)
            record['location'] = l.encode('utf-8').strip().lower().lstrip().rstrip()
         else:
            m = patternMap[recordType]['seller'].match(line)
            if m and not record['seller']:
               #print m.group(1)
               record['seller'] = sanatizers.Seller(m.group(1))
      
         #print ''
      
      print(record)
      #m = descPattern.match(details)
      #if m:
      #    record['details'] = m.group(1).encode('utf-8').strip()
      
      #print(json.dumps(record))
      
      #sys.exit(0)

      cursor = dbconn.context.cursor()
      
      data = open('etc/locations.json', 'r').read()
      locations = json.loads(data)
      
      query = 'INSERT IGNORE INTO sellers (user, location, country) VALUES (%s,%s,%s)'
      
      foundLocation = False
      for loc in locations:
         if record['location'].endswith(loc.encode('utf-8').strip().lower()):
            data = (
               record['seller'],
               record['location'],
               loc.lower().encode('utf-8').strip()
            )
            #print(data)
            cursor.execute(query, data)
            foundLocation = True
            break
      
      # handle cases where the location is not actually a valid format...
      if not foundLocation:
         loc = ''
         m = zipcodePattern.match(record['location'])
         if m:
            loc = 'united states'
         else:
            loc = record['location'].encode('utf-8').strip().lower()

         data = (
            record['seller'],
            record['location'],
            loc
         )
         cursor.execute(query, data)


      dbconn.context.commit()
      
      cursor.close()
      

      
