#!/usr/bin/env python

import amap.mapping as am
import pybitcointools as bc

print("Initialise the mapping object and add assets")
print("Set 2-of-3 multisig policy")

map_obj = am.MapDB(2,3)

print(" ")

print("Add an asset: ref: 757628 year: 2016 man: Acme mass: 400.031")
token_id1 = bc.sha256('ref: 757628 year: 2016 man: Acme')
print("Dummy token ID:")
print("  "+token_id1)

map_obj.add_asset(757628,2016,400.031,token_id1,"Acme")

print("Add an asset: ref: 455952 year: 2017 man: Acme mass: 398.487")
token_id2 = bc.sha256('ref: 455952 year: 2017 man: Acme')
print("Dummy token ID:")
print("  "+token_id2)

map_obj.add_asset(455952,2017,398.487,token_id2,"Acme")

print("Add an asset: ref: 970127 year: 2018 man: Acme mass: 402.968")
token_id3 = bc.sha256('ref: 970127 year: 2018 man: Acme')
print("Dummy token ID:")
print("  "+token_id3)

map_obj.add_asset(970127,2018,402.968,token_id3,"Acme")

print("Add an asset: ref: 875036 year: 2017 man: Acme mass: 401.554")
token_id4 = bc.sha256('ref: 875036 year: 2017 man: Acme')
print("Dummy token ID:")
print("  "+token_id4)

map_obj.add_asset(875036,2017,401.554,token_id4,"Acme")

map_obj.print_json()

print("Add an asset that is already in the object:")
map_obj.add_asset(875036,2017,391.673,token_id4,"Acme")

print(" ")

print("Total mass: "+str(map_obj.get_total_mass()))

print("Remove an asset")
map_obj.remove_asset("455952-2017")
print("Total mass: "+str(map_obj.get_total_mass()))
map_obj.print_json()

print("Add an asset: ref: 553194 year: 2017 man: Acme mass: 405.392")
token_id5 = bc.sha256('ref: 553194 year: 2017 man: Acme')
print("Dummy token ID:")
print("  "+token_id5)

map_obj.add_asset(553194,2017,405.392,token_id5,"Acme")
print("Total mass: "+str(map_obj.get_total_mass()))
map_obj.print_json()
