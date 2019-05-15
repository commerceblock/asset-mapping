#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
import amap.rpchost as rpc
from datetime import datetime
import json
import time
import sys
import os

#key file directory
keydir = "/Users/ttrevethan/asset-mapping/coordinator/keys/"

#object directory for import and export of json objects
objdir = "/Users/ttrevethan/asset-mapping/coordinator/obj/"

#controller number
ncontrol = 1

#version byte is 111 for testnet, 0 for mainnet
version_byte = 111

#the reissuance token is hard coded to the federation block-signing script
reissuanceToken = "3QQWTxbajpCpBxL7wsSvBbwJB5YMiAKJPs"

rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)

print("Sign issuance transactions and mapping object")
print(" ")

map_obj = am.MapDB(2,3)
map_obj.load_json(objdir+'map_us.json')
fmass = map_obj.get_total_mass()
print("    Total mass: "+str("%.3f" % fmass))
print("    Timestamp: "+str(map_obj.get_time())+" ("+datetime.fromtimestamp(map_obj.get_time()).strftime('%c')+")")
print("    Blockheight: "+str(map_obj.get_height()))

print("Load the controller pubkeys")

with open(keydir+'p2sh.json','r') as file:
    p2sh = json.load(file)
con_keys = am.ConPubKey()
con_keys.load_json(keydir+'controllers.json')
key_list = con_keys.list_keys()
print(" ")

print("Load the partially signed transaction")
with open(objdir+'tx_us.json','r') as file:
    partial_tx = json.load(file)

print(" ")
print("Connecting to Ocean client")
print(" ")
ocean = rpc.RPCHost(url)

print(" ")
print("Confirm token issuances:")
print(" ")

numiss = int(partial_tx["numiss"])
for issit in range(numiss):
    decode_tx = ocean.call('decoderawtransaction',partial_tx[str(issit)]["rawtx"])
    txTokenAmount = decode_tx["vin"][0]["issuance"]["assetamount"]
    print("   transaction tokens = "+str("%.8f" % txTokenAmount))

print(" ")
inpt = input("Confirm token issuances correct? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

print(" ")
print("Confirm addresses:")
print(" ")

for issit in range(numiss):
    decode_tx = ocean.call('decoderawtransaction',partial_tx[str(issit)]["rawtx"])
    print("    Issuance address: "+decode_tx["vout"][0]["scriptPubKey"]["addresses"][0])

inpt = input("Addresses correct? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

#hard-coded address for the block-signing script
for issit in range(numiss):
    decode_tx = ocean.call('decoderawtransaction',partial_tx[str(issit)]["rawtx"])
    if decode_tx["vout"][1]["scriptPubKey"]["addresses"][0] != reissuanceToken:
        print("WARNING: re-issuance address is not the block-signing script")
        inpt = input("Proceed? ")
        print(" ")
        if str(inpt) != "Yes":
            print("Exit")
            sys.exit()
print(" ")

print("Add partial signature to issuance transactions")
privkey = open(keydir+'privkey.dat','r').read()
#encode private key to be importable to client
pk_wif = bc.encode_privkey(privkey,'wif_compressed',version_byte)
print(" ")

pSigTxList = {}
for issit in range(numiss):
    partial_sig_tx = ocean.call('signrawtransaction',partial_tx[str(issit)]["rawtx"],[{"txid":partial_tx[str(issit)]["txid"],"vout":int(partial_tx[str(issit)]["vout"]),"scriptPubKey":partial_tx[str(issit)]["scriptPubKey"],"redeemScript":p2sh["redeemScript"]}],[pk_wif])
    partial_sig_tx["txid"] = partial_tx[str(issit)]["txid"]
    partial_sig_tx["vout"] = int(partial_tx[str(issit)]["vout"])
    partial_sig_tx["mass"] = partial_tx[str(issit)]["mass"]
    if partial_sig_tx["complete"]:
        print("    Signatures complete and valid")
        pSigTxList[str(issit)] = partial_sig_tx
    else:
        print("    Signatures not complete")
        pSigTxList[str(issit)] = partial_sig_tx

pSigTxList["numiss"] = str(numiss)

with open(objdir+"tx_ps.json",'w') as file:
    json.dump(pSigTxList,file)

print(" ")
print("Add signature to mapping object:")
map_obj.sign_db(privkey,ncontrol)
print(" ")

map_obj.export_json(objdir+"map_ps.json")

print("Partially signed objects exported to map_ps.json and tx_ps.json in directory "+objdir)
