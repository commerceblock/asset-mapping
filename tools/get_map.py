#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json
import boto3
import sys

print("Load the mapping object - connecting to S3")
s3 = boto3.resource('s3')
s3.Bucket('cb-mapping').download_file('map.json','map.json')
print(" ")

map_obj = am.MapDB(2,3)
map_obj.load_json('map.json')

print("      Asset          Mass                                 Token ID                              ")
print("------------------------------------------------------------------------------------------------")

map_dict = map_obj.get_json()

for i,j in map_dict["assets"].items():
    mass = j["mass"]
    token = j["tokenid"]
    ref = j["ref"]
    print(ref+"    "+str("%.3f" % mass)+"     "+token)

print(" ")
fmass = map_obj.get_total_mass()
print("    Total mass: "+str(fmass))
print(" ")

con_keys = am.ConPubKey()
con_keys.load_json('controllers.json')
key_list = con_keys.list_keys()
if map_obj.verify_multisig(key_list):
    print("    Signatures verified")
else:
    print("    Verification failed")
print(" ")