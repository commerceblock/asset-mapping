#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
import boto3

print("Initialise the mapping object")
print("Set 2-of-3 multisig policy")

map_obj = am.MapDB(2,3)
map_obj.update_time()

print(" ")

print("Export object")
map_obj.export_json('map.json')
print("Upload to S3")
s3 = boto3.resource('s3')
s3.Object('gtsa-mapping','map.json').put(Body=open('map.json','rb'))
