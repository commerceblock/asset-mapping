#!/usr/bin/env python                                              
import amap.mapping as am
import pybitcointools as bc

print("Load the mapping object")

map_obj = am.MapDB(2,3)

map_obj.load_json('map.json')

map_obj.print_json()

print("Load the controler public keys")

con_keys = am.ConPubKey()
con_keys.load_json('controllers.json')

key_list = con_keys.list_keys()

print("Verify signatures of mapping object against pubkeys")

if map_obj.verify_multisig(key_list):
    print("Signatures verified")
else:
    print("Verification failed")
