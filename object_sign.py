#!/usr/bin/env python                                              
import amap.mapping as am
import pybitcointools as bc

print("Load the mapping object")

map_obj = am.MapDB(2,3)

map_obj.load_json('map.json')

map_obj.print_json()

print("Read in controller private keys from file")

c1_privkey = open('c1_privkey.dat','r').read()
c2_privkey = open('c2_privkey.dat','r').read()
c3_privkey = open('c3_privkey.dat','r').read()

print("Update time-stamp")

map_obj.update_time()

map_obj.print_json()

print("Add controller 1 signature")
map_obj.sign_db(c1_privkey,1)

print("Add controller 3 signature")
map_obj.sign_db(c3_privkey,3)

map_obj.print_json()

map_obj.export_json('map.json')
