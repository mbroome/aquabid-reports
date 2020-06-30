import os
import sys
import re

idPattern = re.compile('(.*)(\d\d\d\d\d\d\d\d\d\d)$')

def Seller(s):
   r = re.sub(r'[^ -~_].*', '', s)
   return(r.encode('utf-8').strip().lower().lstrip().rstrip())

def ID(s):
   id = ''
   category = ''

   if '&' in s:
      parts = s.split('&')
      category = parts[0]
      id = parts[1]
   else:
      m = idPattern.match(s)
      if m:
         #print 'matched'
         category = m.group(1)
         id = m.group(2)

   #print id, category
   return(id, category)

