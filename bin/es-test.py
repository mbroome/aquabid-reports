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

def set_data(inputFile, indexName, docType):
   content = open(inputFile, 'r').read()
   data = json.loads(content)

   for rec in data:
      #pp.pprint(rec)
      id = '%s_%s' % (rec['category'], rec['id'])
      yield {'_index': indexName,
             '_type': 'auction',
             '_id': id,
             '_op_type': 'update',
             '_source': {'doc': rec, 'upsert': {'doc': rec}}
            }

indexData = es.indices.stats('_all')
pp.pprint(indexData)

indexName = 'auctions'
docType = 'auctions'
if not es.indices.exists(indexName):
   request_body = {
       "settings" : {
           "number_of_shards": 1,
           "number_of_replicas": 0
       }
   }
   res = es.indices.create(index=indexName, body=request_body)
   pp.pprint(res)

try:
   success, _ = elasticsearch.helpers.bulk(es, set_data('active.json', indexName, docType))
except elasticsearch.ConnectionError, e:
   print '############################'
   pp.pprint(e)
   print


