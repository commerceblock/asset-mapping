#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc

print("Initialise the mapping object and add assets")
print("Set 2-of-3 multisig policy")

map_obj = am.MapDB(2,3)

print(" ")

print("Export object")
map_obj.export_json('map.json')
