#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json
import sys
import requests
import boto3

# Connecting to Ocean client
rpcport = 8332
rpcuser = 'ocean'
rpcpassword = 'oceanpass'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

# function to determine the assets available for redemption and the required tokens
# returns the current blockheight, the current mass-to-token ratio and an array of available asset objects
def get_available_assets():
	#Load the mapping object
    req = requests.get('https://s3.eu-west-1.amazonaws.com/gtsa-mapping/map.json')
    s3 = boto3.resource('s3')
    s3.Bucket('cb-mapping').download_file('rassets.json','rassets.json')

    req_ra = requests.get('https://s3.eu-west-1.amazonaws.com/gtsa-mapping/rassets.json')

    map_obj = am.MapDB(2,3)
    map_obj.init_json(req.json())

    #load the controller public keys
    con_keys = am.ConPubKey()
    con_keys.load_json('controllers.json')
    key_list = con_keys.list_keys()

    if not map_obj.verify_multisig(key_list):
        print("Signature verification failed")

    r_obj = req_ra.json()

    chaininfo = ocean.call('getblockchaininfo')
    blkh = int(chaininfo["blocks"])
    token_ratio = round(am.token_ratio(blkh),13)

    available_assets = []
    for asset in r_obj["assets"]:
        available_asset = {}
        ref = asset["ref"]
        lck = asset["lock"]
        if not lck:
            mass = map_obj.get_mass_assetid(ref)
            exptoken = am.token_amount(blkh,mass)
            ref_comp = ref.split("-")
            available_asset["serialno"] = ref_comp[0]
            available_asset["year"] = ref_comp[1]
            available_asset["manufacturer"] = ref_comp[2]
            available_asset["mass"] = mass
            available_asset["tokens"] = exptoken
            available_assets.append(available_asset)

    return blkh, token_ratio, available_assets

# test the get_available_assets function

bheight,mratio,available = get_available_assets()

print("Block height: "+str(bheight))
print("Mass to token ratio: "+str(mratio))
print(" ")
print("Assets available for redemption: ")
print(" ")
for asset in available:
	print(asset)

reissue_count = 480 - int(bheight) % 480
print("This token amount is valid for the next "+str(reissue_count)+" blocks (minutes)")

