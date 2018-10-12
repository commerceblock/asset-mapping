#!/usr/bin/env python

import amap.mapping as am
import pybitcointools as bc
from datetime import datetime
import amap.rpchost as rpc
import time
import boto3
import sys
import json

print("Redemption of tokens for a specified asset")

print(" ")
print("Controller 2: Confirmer")
print(" ")

print("Load the current mapping object - connecting to S3")
s3 = boto3.resource('s3')
s3.Bucket('cb-mapping').download_file('map.json','map.json')

map_obj = am.MapDB(2,3)
map_obj.load_json('map.json')
fmass = map_obj.get_total_mass()
print("    Total mass: "+str(fmass))
print("    Timestamp: "+str(map_obj.get_time())+" ("+datetime.fromtimestamp(map_obj.get_time()).strftime('%c'))
con_keys = am.ConPubKey()
con_keys.load_json('controllers.json')
key_list = con_keys.list_keys()
if map_obj.verify_multisig(key_list):
    print("    Signatures verified")
else:
    print("    Verification failed")
print(" ")

print("Load the updated mapping object from file")
new_map_obj = am.MapDB(2,3)
new_map_obj.load_json('ps1_map.json')
nmass = map_obj.get_total_mass()
print("    Mass difference: "+str(nmass-fmass))
print("    Timestamp: "+str(map_obj.get_time())+" ("+datetime.fromtimestamp(map_obj.get_time()).strftime('%c'))
print(" ")
print("Create comparison report")
print(" ")
am.diff_mapping(map_obj,new_map_obj)
print(" ")
print("Confirm:")
print("    Changed entries consistent with redemption")
print("    Amounts correct")
print(" ")

inpt = input("Confirm diff data correct?")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

print("Redemption Info:")
rdate = datetime(2018, 9, 7, 0, 2)
print("    Redemption date: "+str(rdate))
print("    Token ratio: "+str(am.token_ratio(rdate)))
print("    Required tokens: "+str(rmass/am.token_ratio(rdate)))
print(" ")
print("Burnt tokens and amounts")
print(" ")
print("    aca8a14cf814d3c7fa5718df157a2229188eef435e45360558ce5a42893979e3: 0.321983253")
print("    6948440932e9544033f985fcca54615babfdfc8e4cac50e76dba468031131c36: 0.678312377")

#add the burnt tokens and amounts to the burnt token list
tokenid = "aca8a14cf814d3c7fa5718df157a2229188eef435e45360558ce5a42893979e3"
btoken1 = []
btoken1.append(tokenid)
btoken1.append(0.321983253)
btoken1.append(new_map_obj.get_mass_tokenid(tokenid))

tokenid = "6948440932e9544033f985fcca54615babfdfc8e4cac50e76dba468031131c36"
btoken2 = []
btoken2.append(tokenid)
btoken2.append(0.678312377)
btoken2.append(new_map_obj.get_mass_tokenid(tokenid))

burnt_tokens = []
burnt_tokens.append(btoken1)
burnt_tokens.append(btoken2)

print(" ")
print("Perform token report and confirm burn against new map")
#perform a token report to determine that the tokens have been successfully burnt
utxorep = ocean.call('getutxoassetinfo')
print("Retrieving UTXO report ...")
map_dict = new_map_obj.get_json()

for btoken in burnt_tokens:
	for entry in utxorep:
    	asset = entry["asset"]
    	if asset == btoken[0]:
    		amount = entry["amountspendable"] + entry["amountfrozen"]
    		print("    TokenID: "+asset)
    		print("        Map mass = "+str(btoken[2]))
    		print("        Chain mass = "+str(amount/am.token_ratio(rdate)))
    		diffr = btoken[2]-amount/am.token_ratio(rdate)
    		print("        Difference = "+str(diffr))
    		if diffr < 0.0:
    			print("ERROR: Excess tokens on chain - check burn")
    			print("Exit")
    			sys.exit()

inpt = input("Confirm report data correct?")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

print(" ")
c1_privkey = open('c2_privkey.dat','r').read()
print("Add signature to mapping object:")
new_map_obj.sign_db(c1_privkey,1)
print(" ")
print("Check signatures")
if new_map_obj.verify_multisig(key_list):
    print("    Signatures verified")
else:
    print("    Signature verification failed")
    print("    ERROR: exit")
    sys.exit()
print(" ")

print("Export fully signed mapping object")
print(" ")
print("     map.json")
map_obj.export_json("map.json")
#upload new map to S3
s3.Object('cb-mapping','map.json').put(Body=open('map.json','rb'))
