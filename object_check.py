#!/usr/bin/env python                                              
import amap.mapping as am
import bitcoin as bc

print("Load the mapping object")

map_obj_old = am.MapDB(2,3)
map_obj_new = am.MapDB(2,3)

map_obj_old.load_json('map.json')
map_obj_new.load_json('map.json')

map_obj_old.print_json()
map_obj_new.print_json()

print("Add a new asset")

print("Add an asset: ref: 837621 year: 2013 man: Acme mass: 399.932")
token_id2 = bc.sha256('ref: 837621 year: 2013 man: Acme')
print("Dummy token ID:")
print("  "+token_id2)

map_obj_new.add_asset(837621,2013,399.932,token_id2,"Acme")

map_obj_new.print_json()

map_obj_new.update_time()

map_obj_new.print_json()

am.diff_mapping(map_obj_new,map_obj_old)
