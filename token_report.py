#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json
import boto3
import sys

print("Token Report")

print("Load the mapping object - connecting to S3")
s3 = boto3.resource('s3')
s3.Bucket('cb-mapping').download_file('map.json','map.json')

map_obj = am.MapDB(2,3)
map_obj.load_json('map.json')
fmass = map_obj.get_total_mass()
print("    Total mass: "+str(fmass))
print(" ")

print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

print("Retrieving UTXO report ...")
utxorep = ocean.call('getutxoassetinfo')
print(" ")
print("Generate report")
print(" ")
token_ratio,hour = am.token_ratio()
print("Token ratio = "+str("%.8f" % token_ratio)+" at hour "+str(hour))
print(" ")
print("Matched tokens:")
print(" ")
print("          Token ID                                                  Mass      Expected-Tokens    Chain-Tokens")
print("-------------------------------------------------------------------------------------------------------------")

map_dict = map_obj.get_json()
extokens = []

for entry in utxorep:
    asset = entry["asset"]
    amount = entry["amountspendable"] + entry["amountfrozen"]
    mass = 0.0
    inmap = False
    for i,j in map_dict["assets"].items():
        if j["tokenid"] == asset:
            mass += j["mass"]
            inmap = True
    if inmap and amount < 999.0:
        exptoken = mass/token_ratio
        print(asset+"   "+str("%.3f" % mass)+"     "+str("%.8f" % exptoken)+"         "+str("%.8f" % amount))
    elif amount < 999.0:
        excluded = []
        excluded.append(asset)
        excluded.append(amount)
        extokens.append(excluded)

if len(extokens) > 0:
    print(" ")
    print("WARNING: Chain tokens not mapped:")
    print(" ")
    print("          Token ID                                                Amount")
    print("------------------------------------------------------------------------")
    for excluded in extokens:
        print(excluded[0]+"   "+str("%.6f" % excluded[1]))
