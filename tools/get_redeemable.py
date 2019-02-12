#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json
import sys
import requests

# Connecting to Ocean client
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

# function to determine the assets available for redemption and the required tokens
# returns the current blockheight, the current mass-to-token ratio and an array of available asset objects
def get_available_assets():
	#Load the mapping object
    req = requests.get('https://s3.eu-west-2.amazonaws.com/cb-mapping/map.json')

    map_obj = am.MapDB(2,3)
    map_obj.init_json(req.json())

    #load the controller public keys
    con_keys = am.ConPubKey()
    con_keys.load_json('controllers.json')
    key_list = con_keys.list_keys()

    if not map_obj.verify_multisig(key_list):
        print("Signature verification failed")

    # Load the redeem list object - rassets.json
    with open('rassets.json') as file:
        r_obj = json.load(file)

    chaininfo = ocean.call('getblockchaininfo')
    blkh = int(chaininfo["blocks"])
    token_ratio = am.token_ratio(blkh)

    available_assets = []
    for asset in r_obj["assets"]:
        available_asset = {}
        ref = asset["ref"]
        lck = asset["lock"]
        if not lck:
            mass = map_obj.get_mass_assetid(ref)
            exptoken = round(mass/token_ratio,8)
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

