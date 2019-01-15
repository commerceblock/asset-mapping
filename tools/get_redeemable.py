#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json
import boto3
import sys

print("Load the redeem list object - connecting to S3")
s3 = boto3.resource('s3')
s3.Bucket('cb-mapping').download_file('rassets.json','rassets.json')
print(" ")
print("Load mapping object")
s3.Bucket('cb-mapping').download_file('map.json','map.json')
print(" ")

map_obj = am.MapDB(2,3)
map_obj.load_json('map.json')

r_obj = {}
with open('rassets.json') as file:
    r_obj = json.load(file)

print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

chaininfo = ocean.call('getblockchaininfo')
blkh = int(chaininfo["blocks"])
token_ratio = am.token_ratio(blkh)
print("Token ratio = "+str("%.8f" % token_ratio)+" at block "+str(blkh))
print(" ")

print("      Asset          Mass            Tokens          Locked   ")
print("--------------------------------------------------------------")

r_dict = r_obj.get_json()

for asset in r_dict["assets"]:
    ref = asset["ref"]
    lck = asset["locked"]
    mass = map_obj.get_mass_assetid(ref)
    exptoken = mass/token_ratio
    print(asset+"   "+str("%.3f" % mass)+"     "+str("%.8f" % exptoken)+"     "+str(lck))
