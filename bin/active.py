#!/usr/bin/env python
import os
import sys
import re
import json
import pprint
pp = pprint.PrettyPrinter(indent=4)

titlePattern = re.compile('<tr .*<b>(.*)<\/b.*tr>')
itemPattern = re.compile('<tr .*?><td .*?>.*<a href=\"(http:\/\/.*?)\">(.*?)<\/a>.*?(<img .*>)<\/font></td><td .*?>.*?>(.*?)<\/font.*?</td><td .*?><font.*?>(.*?)<\/font.*></td><td .*?><font .*?>(.*?)<\/.*</td><td .*?><font.*?>(.*?)<img.*\/reserve_(.*)\.gif.*?</td><\/tr>')
itemNoImagePattern = re.compile('<tr .*?><td .*?>.*<a href=\"(http:\/\/.*?)\">(.*?)<\/a>.*?<\/font></td><td .*?>.*?>(.*?)<\/font.*?</td><td .*?><font.*?>(.*?)<\/font.*></td><td .*?><font .*?>(.*?)<\/.*</td><td .*?><font.*?>(.*?)<img.*\/reserve_(.*)\.gif.*?</td><\/tr>')

content = open('active.html', 'r').read()
section = ''
found = False

activeList = []
bidList = []
for line in content.split('\n'):
   if '<tbody>' in line and 'Item' in line:
      found = True
   if found:
      record = {
                'id': '',
                'section': section,
                'link': '',
                'item': '',
                'pic': '',
                'seller': '',
                'closes': '',
                'bids': '',
                'price': '',
                'reserve': '',
                'shipping': '',
               }

      if '</tbody></table>' in line:
         found = False
      else:
         line = line.replace('&amp;', '&')
         line = line.replace('&nbsp;', ' ')
         line = line.replace('nbsp', ' ')
         m = itemPattern.match(line)
         if m:
            record['link'] = m.group(1)
            record['item'] = m.group(2)
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
            else:
               i = itemNoImagePattern.match(line)
               if i:
                  record['link'] = i.group(1)
                  record['item'] = i.group(2)
                  record['seller'] = i.group(3)
                  record['closes'] = i.group(4)
                  record['bids'] = i.group(5)
                  record['price'] = i.group(6)
                  record['reserve'] = i.group(7)

               else:
                  if '<tbody>' not in line:
                     print 'XXXX: %s' % line

         if record['item']:
            # sanatize the data since it's all over the place
            id = record['link'][record['link'].find('?') + 1:]
            id = id[id.find('&') + 1:]
            record['id'] = id

            if 'buyitnow' in record['bids']:
               record['bids'] = 'buyitnow'
            elif 'No Bids' in record['bids']:
               record['bids'] = '0'

            picData = record['pic']
            if '/us.gif' in picData:
               record['shipping'] = 'us'
            elif '/intlship.gif' in picData:
               record['shipping'] = 'intl'
            elif '/pu.gif' in picData:
               record['shipping'] = 'pickup'

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
            activeList.append(record)
            try:
               bidCount = int(record['bids'])
               #print bidCount
               if bidCount > 0:
                  bidList.append(record)
            except:
               pass

print json.dumps(activeList)
#print json.dumps(bidList)
