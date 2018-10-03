#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
import amap.rpchost as rpc
import json

print("Issue an asset: 2-of-3 controller multisig")
print(" ")
print("Controller 2")
print(" ")
print("Controller 2: Load the initial mapping object")

map_obj = am.MapDB(2,3)
map_obj.load_json('map.json')
fmass = map_obj.get_total_mass()
print("    Total mass: "+str(fmass))
print(" ")
print("Controller 2: Load the new mapping object")
new_map_obj = am.MapDB(2,3)
new_map_obj.load_json('ps1_map.json')
print(" ")
print("    Create comparison report")
print(" ")
am.diff_mapping(map_obj,new_map_obj)
print(" ")
print("    Confirm:")
print("             New entry consistent")
print("             Amounts correct")
print("             Destination addresses correct")
print(" ")

print("Controller 2: Load the P2SH address")

with open('p2sh.json','r') as file:
    p2sh = json.load(file)
print(" ")

print("Controller 2: Load the raw transaction")
with open('ps1_tx.json','r') as file:
    partial_tx = json.load(file)

print("     Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

print("     Confirm token issuance amount:")
assetMass = 403.7814
tgr,hour = am.tgr()
tokenAmount = assetMass/tgr
print("        tokens now = "+str(tokenAmount))
print(" ")
decode_tx = ocean.call('decoderawtransaction',partial_tx["hex"])
txTokenAmount = decode_tx["vin"][0]["issuance"]["assetamount"]
print("        tx tokens = "+str(txTokenAmount))

print("     Add partial signature to issuance transaction:")
c2_privkey = open('c2_privkey.dat','r').read()
#version byte is 239 for ocean regtest mode
version_byte = 239-128
#encode private key to be importable to client
c2_pk_wif = bc.encode_privkey(c2_privkey,'wif_compressed',version_byte)

full_sig_tx = ocean.call('signrawtransaction',partial_tx["hex"],[{"txid":partial_tx["txid"],"vout":int(partial_tx["vout"]),"scriptPubKey":partial_tx["scriptPubKey"],"redeemScript":p2sh["redeemScript"]}],[c2_pk_wif])
print(" ")

print("     Online device: Submit transaction to Ocean network")
submit_tx = ocean.call('sendrawtransaction',full_sig_tx["hex"])
print("        txid: "+str(submit_tx))

print("     Add signature to mapping object:")
new_map_obj.sign_db(c2_privkey,2)
print(" ")
print("     Export fully signed data objects")
new_map_obj.export_json("fs12_map.json")
with open("fs12_tx.json",'w') as file:
          json.dump(full_sig_tx,file)

