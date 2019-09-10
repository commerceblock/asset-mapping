#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
import amap.rpchost as rpc
import json
import time
import sys
import os
from datetime import datetime

#key file directory
keydir = os.getenv('KEYDIR', default="")

#object directory for import and export of json objects
objdir = os.getenv('OBJDIR', default="")

#controller number
ncontrol = 2

#version byte is 111 for testnet, 0 for mainnet
version_byte = 0

rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)

print("Sign issuance transactions and mapping object")
print(" ")

map_obj = am.MapDB(2,3)
map_obj.load_json(objdir+'map_ps.json')
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
with open(objdir+'tx_ps.json','r') as file:
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
    decode_tx = ocean.call('decoderawtransaction',partial_tx[str(issit)]["hex"])
    txTokenAmount = decode_tx["vin"][0]["issuance"]["assetamount"]
    print("   transaction tokens = "+str("%.8f" % txTokenAmount))

print(" ")
inpt = input("Confirm token issuances correct? ")
print(" ")
if str(inpt) != "Yes":
    inpt = input ("Response not recognised. Please type 'Yes' to continue. ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

print(" ")
print("Confirm addresses:")
print(" ")

for issit in range(numiss):
    decode_tx = ocean.call('decoderawtransaction',partial_tx[str(issit)]["hex"])
    print("    Issuance address: "+decode_tx["vout"][0]["scriptPubKey"]["addresses"][0])

inpt = input("Addresses correct? ")
print(" ")
if str(inpt) != "Yes":
    inpt = input ("Response not recognised. Please type 'Yes' to continue. ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

#hard-coded address for the block-signing script
for issit in range(numiss):
    decode_tx = ocean.call('decoderawtransaction',partial_tx[str(issit)]["hex"])
    if decode_tx["vout"][1]["scriptPubKey"]["addresses"][0] != p2sh["reissuanceToken"]:
        print("WARNING: re-issuance address is not the block-signing script")
        inpt = input("Proceed? ")
        print(" ")
        if str(inpt) != "Yes":
            inpt = input ("Response not recognised. Please type 'Yes' to continue. ")
        if str(inpt) != "Yes":
            print("Exit")
            sys.exit()
print(" ")

print("Add partial signature to issuance transactions")
privkey = open(keydir+'privkey.dat','r').read()
#encode private key to be importable to client
pk_wif = bc.encode_privkey(privkey,'wif_compressed',version_byte)
print(" ")

fSigTxList = []
for issit in range(numiss):
    full_sig_tx = ocean.call('signrawtransaction',partial_tx[str(issit)]["hex"],[{"txid":partial_tx[str(issit)]["txid"],"vout":int(partial_tx[str(issit)]["vout"]),"scriptPubKey":p2sh["scriptPubKey"],"redeemScript":p2sh["redeemScript"]}],[pk_wif])
    full_sig_tx["txid"] = partial_tx[str(issit)]["txid"]
    full_sig_tx["vout"] = int(partial_tx[str(issit)]["vout"])
    full_sig_tx["mass"] = partial_tx[str(issit)]["mass"]
    if full_sig_tx["complete"]:
        print("    Signatures complete and valid")
        fSigTxList.append(full_sig_tx)
    else:
        print("    Signatures not complete")
        fSigTxList.append(full_sig_tx)

with open(objdir+"tx_fs.json",'w') as file:
    json.dump(fSigTxList,file)

print(" ")
print("Add signature to mapping object:")
map_obj.sign_db(privkey,ncontrol)
print(" ")
print("Check signatures")
if map_obj.verify_multisig(key_list):
    print("    Signatures complete and valid")
else:
    print("    Signatures not complete")
    print("Exit")
    sys.exit()
print(" ")

map_obj.export_json(objdir+"map_fs.json")

print("Fully signed objects exported to map_fs.json and tx_fs.json in directory "+objdir)
