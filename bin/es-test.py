#!/usr/bin/env python
import os
import sys
import json
import logging

import elasticsearch
import elasticsearch.helpers
import certifi

logging.basicConfig(level=logging.INFO)

import pprint
pp = pprint.PrettyPrinter(indent=4)

import urllib3
urllib3.disable_warnings()

es = elasticsearch.Elasticsearch(['https://ro569ymesw:zvy11q9ajr@first-cluster-2318734906.us-east-1.bonsaisearch.net:443'], use_ssl=True, ca_certs=certifi.where())

#pp.pprint(es)

indexData = es.indices.stats('_all')
pp.pprint(indexData)

content = open('active.json', 'r').read()
data = json.loads(content)

bulkMax = 500
indexName = 'auctions'

if not es.indices.exists(indexName):
   # since we are running locally, use one shard and no replicas
   request_body = {
       "settings" : {
           "number_of_shards": 1,
           "number_of_replicas": 0
       }
   }
   res = es.indices.create(index=indexName, body=request_body)
   pp.pprint(res)

request = []
for rec in data:
   #pp.pprint(rec)
   id = '%s_%s' % (rec['category'], rec['id'])
   request.append({'_index': indexName,
                   '_type': 'auction',
                   '_id': id,
                   '_source': rec})
   
   if len(request) >= bulkMax:
      #pp.pprint(request)
      try:
         res = elasticsearch.helpers.bulk(es, request, chunk_size=500)
         pp.pprint(res)
      except elasticsearch.ConnectionError, e:
         print '############################'
         pp.pprint(e)
         print

      request = []

# any left after the loop, load them
if len(request):
   #pp.pprint(request)
   try:
      res = elasticsearch.helpers.bulk(es, request, chunk_size=len(request))
      pp.pprint(res)
   except elasticsearch.ConnectionError, e:
      print '############################'
      pp.pprint(e)
      print

