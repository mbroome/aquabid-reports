import re
import time
import pytz
import datetime
import dateutil
import dateutil.parser

import pprint
pp = pprint.PrettyPrinter(indent=4)

TZINFOS = {
    'CDT': pytz.timezone('US/Central'),
}

to_zone = dateutil.tz.tzlocal()

cdtPattern = re.compile('(\w+) (\w+) (\d+) (\d+) - (\d+:\d+:\d+) (\w+) (\w+)')

# dates suck to parse
def parseTimestamp(timestamp):
   unixtime = None
   utc = None
   #print timestamp
   # is this a funky timestamp in CDT format...
   m = cdtPattern.match(timestamp)
   if m:
      ft = '%s %s %s, %s %s' % (m.group(5), m.group(2), m.group(3), m.group(4), m.group(7))
      #print ft
      # parse as the CDT timezone
      t = dateutil.parser.parse(ft, tzinfos=TZINFOS)
      #pp.pprint(t)
      # utc the time
      utc = t.astimezone(pytz.utc)
      #pp.pprint(utc)
      # localtime the time
      lt = utc.astimezone(to_zone)
      #pp.pprint(lt)
      # unixtime the time
      unixtime = time.mktime(lt.timetuple())
      #pp.pprint(unixtime)

   else:
      try:
         unixtime = int(timestamp)
         #pp.pprint(unixtime)
         dt = datetime.datetime.fromtimestamp(unixtime, tz=to_zone)
         utc = dt.astimezone(pytz.utc)
         #pp.pprint(utc)
      except Exception, e:
         pp.pprint(e)

   return(unixtime, utc)
