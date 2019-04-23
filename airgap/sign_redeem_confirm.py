#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
import amap.rpchost as rpc
from datetime import datetime
import json
import time
import sys
import os

#controller number
ncontrol = 2

print("Sign mapping object")
print(" ")

map_obj = am.MapDB(2,3)
map_obj.load_json('map_us.json')
fmass = map_obj.get_total_mass()
print("    Total mass: "+str("%.3f" % fmass))
print("    Timestamp: "+str(map_obj.get_time())+" ("+datetime.fromtimestamp(map_obj.get_time()).strftime('%c')+")")
print("    Blockheight: "+str(map_obj.get_height()))

print("Load the controller pubkeys")

with open('key/p2sh.json','r') as file:
    p2sh = json.load(file)
con_keys = am.ConPubKey()
con_keys.load_json('key/controllers.json')
key_list = con_keys.list_keys()
print(" ")

privkey = open('key/privkey.dat','r').read()

print(" ")
print("Add signature to mapping object:")
map_obj.sign_db(privkey,ncontrol)
print(" ")

map_obj.export_json("map_fs.json")

print("Fully signed mapping objects exported to map_fs.json in directory "+os.getcwd())
