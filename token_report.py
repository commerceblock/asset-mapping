#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json

print("Token Report")

print("Load the mapping object")

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
tgr,hour = am.tgr()
print("TGR = "+str("%.6f" % tgr)+" at hour "+str(hour))
print(" ")
print("          Token ID                                                    Mass      Ex-Tokens    Chain-Tokens")
print("-----------------------------------------------------------------------------------------------------------")

map_dict = map_obj.get_json()

for entry in utxorep:
    asset = entry["asset"]
    amount = entry["amountspendable"] + entry["amountfrozen"]
    mass = 0.0
    inmap = False
    for i,j in map_dict["assets"].items():
        if j["tokenid"] == asset:
            mass += j["mass"]
            inmap = True
    if inmap:
        exptoken = mass/tgr
        print(asset+"  "+str("%.3f" % mass)+"   "+str("%.6f" % exptoken)+"   "+str("%.6f" % amount))
