#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import requests
import json
import boto3
import sys

print("Load the mapping object - connecting to S3")
print(" ")

req = requests.get('https://s3.eu-west-1.amazonaws.com/gtsa-mapping/map.json')

map_obj = am.MapDB(2,3)
map_obj.init_json(req.json())

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

print("Export asset map as CSV file: map.csv")

map_obj.export_csv("map.csv")
