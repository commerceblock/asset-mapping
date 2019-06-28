#!/usr/bin/env python

import amap.mapping as am
import amap.rpchost as rpc
import json
import sys

print("Aggregate controller public keys and P2SH generation")
print(" ")

controller_pub_keys = []

c1_public = input("Enter the public key of controller 1: ")
if len(c1_public) != 66:
    print("ERROR: public key format error - must be compressed")
    print("Exit")
    sys.exit()

controller_pub_keys.append(c1_public)
print(" ")

c2_public = input("Enter the public key of controller 2: ")
if len(c2_public) != 66:
    print("ERROR: public key format error - must be compressed")
    print("Exit")
    sys.exit()

controller_pub_keys.append(c2_public)
print(" ")

c3_public = input("Enter the public key of controller 3: ")
if len(c3_public) != 66:
    print("ERROR: public key format error - must be compressed")
    print("Exit")
    sys.exit()
    
controller_pub_keys.append(c3_public)
print(" ")

print("Creating controller object with 2 of 3 policy")
con_obj = am.ConPubKey(2,3,controller_pub_keys)

print("Exporting object to file")
con_obj.export_json('controllers.json')
print(" ")

print("Print object")
con_obj.print_keys()
print(" ")

print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

print("Creating 2-of-3 multisig address from the controller public keys")
result = ocean.call('createmultisig',2,controller_pub_keys)
print(" ")

validate = ocean.call('validateaddress',result['address'])
result['scriptPubKey'] = validate['scriptPubKey']

print("P2SH address: "+result['address'])
print(" ")
print("Redeem script: "+result['redeemScript'])
print(" ")
print("scriptPubKey: "+result['scriptPubKey'])
print(" ")

print("CHECK: address encoding and prefix matches network settings")
print(" ")
print("Exporting P2SH data to p2sh.json")
with open('p2sh.json','w') as file:
    json.dump(result,file)
